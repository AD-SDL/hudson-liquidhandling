#/usr/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Illegal number of parameters" >&2
    echo "Pass in basename of the hidex file" >&2
    echo "for example: ${0} Campaign1_20211006_174300_RawOD"
    exit 2
fi


IN=$1
paste $IN"_rows.csv" $IN"_data.csv" > $IN".plot"
cat $IN".plot" | perl add_plot_labbels.py > $IN".plot.gnuplot"
