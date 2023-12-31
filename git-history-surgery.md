# how to extract a subdirectory of git history
```
    cd; rm -rf letz/; git clone src/letz; cd letz
    export FILTER_BRANCH_SQUELCH_WARNING=1

    # move zap.py -> py/zap.py
    #   it originated there since it was so overall in its scope
    git filter-branch --tree-filter 'if [ -f "zap.py" ]; then mkdir -p py && mv zap.py py/zap.py; fi' --prune-empty --tag-name-filter cat -- --all

    # remove not in py/
    git filter-branch -f --index-filter 'git rm --cached -qr --ignore-unmatch $(git ls-files | grep -v "^py/")' --prune-empty --tag-name-filter cat -- --all
    # burst py/
    git filter-branch -f --subdirectory-filter py --prune-empty --tag-name-filter cat -- --all
    
    # remove other random files that were in py/
    git filter-branch -f --tree-filter ' rm -rf r* \
        rm -rf R* \
        rm -rf C* \
        rm -rf s*' --prune-empty -- --all


    # extract just the main branch to a new repository using the following commands:

    git checkout main
    git clone . zap
```
