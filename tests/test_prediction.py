import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError

spec = importlib.util.spec_from_file_location('prediction_server', Path(__file__).resolve().parents[1] / 'experiments/response-prediction/server.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class LabTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.calls = []
        def predict(messages):
            self.calls.append(messages)
            return 'Synthetic prediction.'
        self.path = Path(self.tmp.name) / 'lab.sqlite3'
        self.lab = module.Lab(self.path, predict)

    def test_prediction_precedes_answer_and_reveal_is_idempotent(self):
        run = self.lab.start()
        self.assertNotIn('prediction', run)
        self.assertNotIn('messages', run)
        self.assertEqual(self.lab.start()['id'], run['id'])
        self.assertEqual(len(self.calls), 1)
        self.assertNotIn('prediction', self.lab.state()['active'])
        self.assertEqual(module.Lab(self.path, lambda _: None).state()['active']['id'], run['id'])
        with self.assertRaises(ValueError):
            self.lab.answer(run['id'], ' ')
        revealed = self.lab.answer(run['id'], 'A unique actual answer.')
        self.assertEqual(revealed['prediction'], 'Synthetic prediction.')
        self.assertLessEqual(revealed['predictedAt'], revealed['answeredAt'])
        self.lab.answer(run['id'], 'A unique actual answer.')
        self.assertEqual(len(self.lab.examples()), 1)
        with self.assertRaises(ValueError):
            self.lab.answer(run['id'], 'Changed after reveal')
        self.assertNotIn('A unique actual answer.', json.dumps(self.calls[0]))
        following = self.lab.start()
        self.assertEqual(following['exampleCount'], 1)
        self.assertIn('A unique actual answer.', json.dumps(self.calls[1]))

    def test_import_dedup_and_repeat_exclusion(self):
        records = [dict(questionId=q['id'], question=q['text'], answer='Example answer', context='', savedAt='2026-11-19') for q in module.QUESTIONS]
        self.lab.import_examples(records)
        self.lab.import_examples(records)
        self.assertEqual(len(self.lab.examples()), len(records))
        run = self.lab.start()
        self.assertTrue(run['repeatedQuestion'])
        prompt = json.loads(self.calls[0][1]['content'])
        self.assertNotIn(run['question']['text'], [e['question'] for e in prompt['earlier_answers']])

    def test_failure_allows_retry_and_scoring_requires_answer(self):
        self.lab.predictor = lambda _: (_ for _ in ()).throw(RuntimeError('Test failure'))
        with self.assertRaises(RuntimeError):
            self.lab.start()
        self.assertFalse(self.lab.generating)
        self.assertIsNone(self.lab.state()['active'])
        self.lab.predictor = lambda _: 'Retry prediction'
        run = self.lab.start()
        with self.assertRaises(ValueError):
            self.lab.score(run['id'], 2)
        self.lab.answer(run['id'], 'Saved')
        self.assertEqual(self.lab.score(run['id'], 2)['score'], 2)
        with self.assertRaises(ValueError):
            self.lab.score(run['id'], True)

    def test_http_restricts_private_files_origin_and_hidden_export(self):
        server = module.make_server(self.lab, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        root = f'http://127.0.0.1:{server.server_port}'
        state = json.load(urlopen(root + '/api/state'))
        headers = {'Content-Type': 'application/json', 'X-Lab-Token': state['token']}
        for path in ['/private/response-prediction/lab.sqlite3', '/experiments/response-prediction/server.py', '/../../private/lab.sqlite3']:
            with self.assertRaises(HTTPError) as err:
                urlopen(root + path)
            self.assertEqual(err.exception.code, 404)
        with self.assertRaises(HTTPError) as err:
            urlopen(Request(root + '/api/start', data=b'{}', headers={**headers, 'Origin': 'https://elsewhere.example'}))
        self.assertEqual(err.exception.code, 403)
        with self.assertRaises(HTTPError):
            urlopen(Request(root + '/api/start', data=b'{}', headers={'Content-Type': 'application/json'}))
        run = json.load(urlopen(Request(root + '/api/start', data=b'{}', headers=headers)))
        self.assertNotIn('prediction', run)
        export = json.load(urlopen(Request(root + '/api/export', headers=headers)))
        self.assertEqual(export['runs'], [])
        revealed = json.load(urlopen(Request(root + '/api/answer', data=json.dumps({'id': run['id'], 'answer': 'HTTP test answer'}).encode(), headers=headers)))
        self.assertEqual(revealed['prediction'], 'Synthetic prediction.')
        export = json.load(urlopen(Request(root + '/api/export', headers=headers)))
        self.assertEqual(len(export['runs']), 1)

if __name__ == '__main__':
    unittest.main()
