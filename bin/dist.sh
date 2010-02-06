#!/bin/bash

VERSION="r2"

function build {
    rm -rf tmp/build
    mkdir -v tmp/build tmp/build/bin tmp/build/doc tmp/build/lib tmp/build/etc tmp/build/test
    cp -r -v bin/* tmp/build/bin
    cp -r -v doc/* tmp/build/doc
    cp -r -v lib/* tmp/build/lib
    cp -r -v etc/* tmp/build/etc
    cp -r -v test/* tmp/build/test
    cp -v setup.sh tmp/build    
}

function make_tarball {
    mkdir -v tmp/dist
    cp -r tmp/build tmp/dist/spiderviz-$VERSION
    cd tmp/dist
    tar cf spiderviz-$VERSION.tar spiderviz-$VERSION
    gzip spiderviz-$VERSION.tar
    cd ../..
    rm -rf tmp/dist/spiderviz-$VERSION
}

function clean {
    rm -rf tmp/build    
}

function make_docs {
    cd sphinx
    rm -rf /tmp/api
    sphinx-build -b html . /tmp/api
    #rsync -a /tmp/api $RSYNC_FIAT_AUTH
    #rm -rf /tmp/api
    cd ..
}

if [ "$1" = "build" ]; then
    build
fi

if [ "$1" = "tarball" ]; then
    build
    make_tarball
fi

if [ "$1" = "docs" ]; then
    make_docs
fi

if [ "$1" = "help" ]; then
    echo "build, tarball, docs, help"
fi
