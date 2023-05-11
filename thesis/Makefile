build:: fonts graphs
	tectonic -Z shell-escape src/main.tex
	mv src/main.pdf Thesis.pdf

fonts::
	./fonts/install.sh

graphs::
	find . -name "*.mmd" | xargs -I % npx -yp @mermaid-js/mermaid-cli mmdc -i % -f -e pdf
