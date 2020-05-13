file_name () {
	filename=$(basename "$1")
	extension="${filename##*.}"
	filename="${filename%.*}"

	echo $filename
}

rm -rf ./wikipedia-pictures-converted
mkdir ./wikipedia-pictures-converted

for f in ./wikipedia-pictures/*
do
  m=$(file_name $f)
  convert $f ./wikipedia-pictures-converted/$m.jpeg
done