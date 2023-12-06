#!/bin/bash

# Clone BAM repositories
for i in {1..147}; do
  git clone https://core-gitlfs.tpi.uni-jena.de/core_database/BAM_$(printf "%04d" $i).git
done

# Clone Hyb repositories
for i in {1..18}; do
  git clone https://core-gitlfs.tpi.uni-jena.de/core_database/Hyb_$(printf "%04d" $i).git
done

# Clone THC repositories
for i in {1..107}; do
  git clone https://core-gitlfs.tpi.uni-jena.de/core_database/THC_$(printf "%04d" $i).git
done

