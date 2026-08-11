# File format support

| Format | Read | Write | Notes |
|---|---:|---:|---|
| TXT/LOG | Yes | Yes | UTF-8, line/head/tail helpers |
| JSON | Yes | Yes | Native hot path; atomic JSON write |
| CSV | Yes | Yes/append/update | Quoting + multiline quoted records |
| INI | Yes | Yes | Practical config support |
| properties | Yes | Yes | Key/value config |
| XML | Yes | Yes/append/find | stdlib dictionary conversion |
| YAML | Yes | Yes | dependency-free practical subset |
| PDF | Basic text | Basic text | not a full PDF engine |
| Markdown/HTML/CSS/JS/RTF/TEX/Python | Text/helper | Yes | convenience functions |
| ZIP | Yes | Yes | stdlib archive helper |
| SQLite | Query | N/A | parameterized `sql_execute` helper |
