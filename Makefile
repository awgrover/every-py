# to make the .mpy packge for circuitpython

# depend on git-controlled files, and their directory to detect dropping a file
all_mpy = $(shell git ls-files | egrep '\.py$$' | sed 's/\.py$$/.mpy/') 
all_dirs = $(shell git ls-files | xargs dirname | sort -u)
version = $(shell python3 -c 'import every.version; print( every.version.__version__)')

every-mpy-$(version).zip : $(all_mpy) $(all_dirs) | git-tag
	echo "MAKE " $(all_mpy)
	# [ -e $@ ] && rm $@
	rm $@ 2>/dev/null || true
	zip $@ $(all_mpy)

%.mpy : %.py | mpy-cross
	mpy-cross $< -o $@

.PHONY : mpy-cross
mpy-cross :
	@# check for the mpy-cross tool
	@ if ! which mpy-cross >/dev/null; then \
		echo "get, install as mpy-cross, and add to PATH: mpy-cross command from https://pypi.org/project/mpy-cross/"; \
		exit 1; \
	fi

.PHONY : git-tag
git-tag :
	@# Check version==git-tag==head
	@if ! git diff-index --quiet HEAD; then \
		git status; \
		echo "Won't make: Uncommited changes"; \
		exit 1; \
	fi
	@if test "`git tag --list v$(version)`" = '' ; then \
		echo "No git-tag matching version.py: v$(version). # git tag v$(version)"; \
		exit 1; \
	fi
	@if test `git show-ref -s --tags v1.0` != `git show-ref --head --heads -s HEAD`; then \
		echo "HEAD != tag v$(version). update version.py"; \
		exit 1; \
	fi
