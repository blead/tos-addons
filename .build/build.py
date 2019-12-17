#!/usr/bin/env python3

import glob
import json
import os
import shutil
import subprocess
import sys

def build():
  INTERMEDIATE_DIR = os.getenv('INTERMEDIATE_DIR', '.tmp')
  OUTPUT_DIR = os.getenv('OUTPUT_DIR', '_out')
  targets_json_path = 'addons.json'

  if len(sys.argv) > 2:
    print('Usage: build.py [targets.json]')
    sys.exit(1)
  if len(sys.argv) == 2:
    print('Reading configuration from {}.'.format(sys.argv[1]))
    targets_json_path = sys.argv[1]

  print('Generating build targets.')

  build_targets = []
  with open(targets_json_path, encoding='utf-8') as f:
    for target in json.load(f):
      if 'file' in target and 'releaseTag' in target:
        tags = subprocess.run(['git', 'tag', '-l', '$tagName == {}'.format(target['releaseTag'])], capture_output=True, encoding='utf-8').stdout
        if tags == '':
          build_targets.append({
            'file': target['file'],
            'tag': target['releaseTag']
          })

  print(f'{len(build_targets)} targets generated.')

  if len(build_targets) > 0:
    os.makedirs(INTERMEDIATE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for target in build_targets:
      source_paths = glob.glob('{}/src/*'.format(target['file']))
      intermediate_subdir_path = '{}/addon_d.ipf/{}'.format(INTERMEDIATE_DIR, target['file'])
      output_path = '{}/{}.ipf'.format(OUTPUT_DIR, target['tag'])

      print('Building {} -> {}.'.format(target['file'], output_path))

      os.makedirs(intermediate_subdir_path, exist_ok=True)
      for source in source_paths:
        shutil.copy2(source, intermediate_subdir_path)
      subprocess.run([sys.executable, '.build/ipf.py', '-c', '-e', '-f', output_path, INTERMEDIATE_DIR])
      shutil.rmtree(intermediate_subdir_path)

    shutil.rmtree(INTERMEDIATE_DIR)

if __name__ == '__main__':
  build()
