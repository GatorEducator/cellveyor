# cellveyor

## Example Command

```
poetry run cellveyor --spreadsheet-directory \
/home/gkapfham/working/data/gradebook/2023 --spreadsheet-file CMPSC-203-Fall-2023-Gradebook.xlsx \
--sheet-name Main \
--key-attribute "Student GitHub" \
--key-value "gkapfham" \
--column-regexp "^(Summary Grade|Final Grade) .*$" \
--feedback-regexp "Summary Grade 1 - Feedback" \
--feedback-file /home/gkapfham/working/teaching/github-classroom/feedback/all/feedback.yml \
--feedback-file /home/gkapfham/working/teaching/github-classroom/feedback/developer-development/feedback-overall-course-assessment.yml \
--github-token <Private GitHub Acess Token> \
--github-organization Allegheny-Computer-Science-203-F2023 \
--github-repository-prefix computer-science-203-fall-2023-course-assessment \
--transfer-report
```
<img src="https://github.com/AstuteSource/chasten/blob/master/.github/images/chasten-logo.svg" alt="Chasten Logo"
    title="Chasten Logo" />
# 💫 chasten

[![build](https://github.com/gkapfham/chasten/actions/workflows/build.yml/badge.svg)](https://github.com/gkapfham/chasten/actions/workflows/build.yml)
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/gkapfham/5300aa276fa9261b2b21b96c3141b3ad/raw/covbadge.json)
[![Language:
Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://github.com/gkapfham/chasten/search?l=python)
[![Code Style: black](https://img.shields.io/badge/Code%20Style-Black-blue.svg)](https://github.com/psf/black)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-blue.svg)](https://github.com/gkapfham/chasten/graphs/commit-activity)
[![License LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
