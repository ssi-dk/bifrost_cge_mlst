# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## v2_2_5 - 2021-04-29
### Changed
- bifrost_cge_mlst/datadump.py
  - sequence_type changed from string to object in summary
## v2_2_4 - 2021-04-16
### Notes
Apparently strain is not the same thing as sequence type, so we changed that.
### Added
### Changed
- bifrost_cge_mlst/datadump.py
  - strain changed to sequence type

## [v2_2_3] - 2021-03-29
### Notes
Minor rehaul of the scuffed version Martin left. Most upgrades in datadump.
### Added
### Changed
- bifrost_cge_mlst/rule__cge_mlst.py
  - fixed shell command
- bifrost_cge_mlst/datadump.py
  - reworked file to bring it up to day with 2.1 conventions regarding lib and schema
- tests/test_simple.py
  - named to test_simple, added a species to the sample so we can do proper testing
 
## [v2_2_1] - 2020-02-24
### Notes
Changes to use the 2_1_0 schema, organizational updates, and updates to tests to make this work. Also updated the scheme for how the docker image is developed on to be from the root for local dev.

### Added
- docs/
  - history.rst
  - index.rst
  - readme.rst
- tests/
  - test_simple.py
- HISTORY.md
- setup.cfg

### Changed
- .dockerignore
- .gitignore
- Dockerfile
- requirements.txt
- setup.py
- bifrost_whats_my_species/
  - \_\_init\_\_.py
  - \_\_main\_\_.py
  - config.yaml
  - datadump.py
  - launcher.py
  - pipeline.smk
- .github/workflows
  - docker_build_and_push_to_dockerhub.yml
  - test_standard_workflow.yml -> run_tests.yml


### Removed
- tests/test_1_standard_workflow.py
- docker-compose.dev.yaml
- docker-compose.yaml
- requirements.dev.txt