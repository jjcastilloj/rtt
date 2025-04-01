DATA_DIR="data/" 
DATA_FILE=$DATA_DIR/$1
date
echo "Data source: "$DATA_FILE
echo "Deleting previous results files..."
find experiments -type f -name "*txt" -delete

./assess --fast --file $DATA_FILE --streams 1 --tests 111111111111111 --defaultpar --fileoutput --binary 1000000
date
