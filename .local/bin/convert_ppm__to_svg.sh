for file in *.ppm; do
    potrace -s "$file" -o "${file%.ppm}.svg"
done
