```bash
# debug
scrapy shell -s USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36" https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006074069/LEGISCTA000006157551/?anchor=LEGIARTI000006796412#LEGIARTI000006796412

# run spider
rm -rf legifrance.csv legifrance.log
scrapy runspider legifrance_scrapper.py -o legifrance.csv --logfile legifrance.log

```