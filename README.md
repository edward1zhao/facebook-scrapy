fb_from_domain.py
=================
Visits all domains provided in input file, and stores its fb page url, if such is found.

You have to provide following params on last line of script:
	- `input_file`: path to input file, this file should contain domains (one domain per line)
	- `output_file`: path where the results of this script will be stored, script writes to this
			 csv file with two columns `fb` which stands for facebook_page_url and `url` 
			 which stands for domain url
	- `concurrency`: how many concurrent requests. Proxies arent needed in this case, since each
			 domain is different

	Recommended: concurrency=500

The output of this script should be used as input for FacebookMapper.py



fb_from_search_engine.py
========================
Leverages search engines to find facebook url from provided domains from input file.

You have to provide followint params on last line of script:
	- `input_file`: path to file which contains domains (1 domain per line)
	- `output_file`: path to output csv file, this will be result of script
			 csv with two columns `fb` which stands for found facebook page url
			 and `url` which stands for domain url
	- `search_engine`: "bing"/"duck"
	- `use_proxy`: True/False
	- `concurrency`: number of concurrent requests

	Recommended: use_proxy=False, concurrency=20, search_engine="bing"

The output of this script should be used as input for FacebookMapper.py


FacebookMapper.py
=================
Visits fb page by its facebook url and parses facebook id

You have to provide following params on last line of script:
	- `input_file`: path to csv output of fb_from_domain.py or fb_from_search_engine.py
			file has to be csv, with 2 columns - `fb`, `url`
	- `output_file`: path where results of this script will be written
	- `use_proxy`: False/True
	- `concurrency`: number of concurrent requests

	Recommened: use_proxy=True, concurrency=333

Output of this script will be csv file, containing 3 columns, `fb` stands for facebook page url, `url` stands for domain url, and `fb_id` which is used as key to add the first two columns to right rows in db

Also output of this script should be used as input in db_import.py


db_import.py
============
Get ouput from FacebookMapper.py as input, and import domain url and facebook page url to according rows in db looked up by facebook id

You have to provide following param in last line of script:
	- "name_of_output_from_facebookmapper.py.csv"


