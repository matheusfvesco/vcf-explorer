
# TODO: add tests for snakemake output structure
# consider datasets: 
# https://ont-exd-int-s3-euwst1-epi2me-labs.s3-eu-west-1.amazonaws.com/vcf_tutorial/ont_hg002/medaka.vcf.gz
# https://wannovar.wglab.org/download/anemia.vcf

# add new sample data as example
# if data/anemia.vcf.gz doesn't exist, download it
#if [ ! -f "data/test.vcf.gz" ]; then
#    echo "Downloading anemia vcf..."
#    # doesnloads https://wannovar.wglab.org/download/anemia.vcf inside data dir
#    wget https://wannovar.wglab.org/download/anemia.vcf -O data/anemia.vcf
#    head -n 200 data/anemia.vcf > data/anemia2.vcf
#    rm -rf data/anemia.vcf
#    mv data/anemia2.vcf data/test.vcf
#    gzip data/test.vcf
#fi

uv run --package api pytest