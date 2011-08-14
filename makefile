# Build file for DIpy

cover : 
	coverage run wsd_ex_parser_test.py
	coverage html
	open htmlcov/wsd_ex_parser.html

test : 
	python wsd_ex_parser_test.py

clean :
	rm -rf *.pyc htmlcov .coverage *.html
