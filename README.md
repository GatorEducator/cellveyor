# cellveyor

## Example Command

[![build](https://github.com/gkapfham/cellveyor/actions/workflows/build.yml/badge.svg)](https://https://github.com/gkapfham/cellveyor/actions/workflows/build.yml)
[![Language:Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://github.com/gkapfham/cellveyor/search?l=python)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-blue.svg)](https://github.com/gkapfham/cellveyor/graphs/commit-activity)

```
poetry run cellveyor
--spreadsheet-directory `directory-to-spreadsheet`
--spreadsheet-file `directory-to-file`
--sheet-name Main \
--key-attribute "Student GitHub" \
--key-value "gkapfham" \
--column-regexp "^(Summary Grade|Final Grade) .*$" \
--feedback-regexp "Summary Grade 1 - Feedback" \
--feedback-file /home/gkapfham/working/teaching/github-classroom/
feedback/all/feedback.yml \
--feedback-file /home/gkapfham/working/teaching/github-
classroom/feedback/developer
-development/feedback-overall-course-assessment.yml \
--github-token <Private GitHub Acess Token> \
--github-organization Allegheny-Computer-Science-203-F2023 \
--github-repository-prefix computer-science-203-fall-2023-course-assessment \
--transfer-report
```
