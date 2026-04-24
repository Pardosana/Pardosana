.PHONY: all build full cheat analysis clean

all: build

build: full cheat

full:
	python3 scripts/build_full.py
	pandoc docs/FULL.md -o docs/FULL.docx
	pandoc docs/FULL.md -o docs/FULL.html --standalone --metadata title="SalesEngine V26.1 FULL"
	python3 -c "from weasyprint import HTML; HTML('docs/FULL.html').write_pdf('docs/FULL.pdf')"

cheat:
	python3 -c "from weasyprint import HTML; HTML('docs/02_OPERATOR_CHEAT_SHEET.html').write_pdf('docs/02_OPERATOR_CHEAT_SHEET.pdf')"

analysis:
	python3 scripts/analyze_calls.py data/Dzivie+zvani.md

clean:
	rm -f docs/FULL.html docs/FULL.pdf docs/FULL.docx
