PAPER = Yong
.DEFAULT_GOAL := all

all:
	pdflatex $(PAPER)
	open $(PAPER).pdf

more:
	pdflatex $(PAPER)
	bibtex $(PAPER)
	pdflatex $(PAPER)
	pdflatex $(PAPER)
	open $(PAPER).pdf

diffmore:
	latexdiff old.tex $(PAPER).tex > diff.tex
	xelatex diff
	bibtex diff
	xelatex diff
	xelatex diff
	open diff.pdf

diff:
	latexdiff old.tex $(PAPER).tex > diff.tex
	xelatex diff
	open diff.pdf

clean:
	@rm -f *.aux || :
	@rm -f *.dvi || :
	@rm -f *.out || :
	@rm -f *.log || :
	@rm -f *.bbl || :
	@rm -f *.blg || :
	@rm -f *.backup || :
	@rm -f *~ || :

	