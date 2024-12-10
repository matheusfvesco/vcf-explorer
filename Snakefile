rule all:
    input:
        expand("{sample}.tsv", sample=["data/NIST"])

rule annotate:
    input:
        "{sample}.vcf.gz"
    output:
        "{sample}.tsv"
    shell:
        "src/annotate.py {input} {output}"