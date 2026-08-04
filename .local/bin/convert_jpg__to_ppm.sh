for f in *.jpg; do
    convert "$f" "${f%.jpg}.ppm"
done
