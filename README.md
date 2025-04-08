# Setup
To get started using this repo you will need to set up a conda environment with the necessary packages.  To do this, navigate to this repo's parent directory and run the following in order:

 - `conda create -n eris python -y`
 - `conda activate eris`
 - `pip install cptac`
 - `conda install pandas matplotlib seaborn requests ipykernel scikit-learn scipy -y`

If you encounter problems creating/employing the environment with the process above, try the following:
 - `conda remove --name eris --all`
 - `conda create -n eris python=3.12 -y`
 - `conda activate eris`
 - `conda install pandas matplotlib seaborn requests ipykernel scikit-learn scipy -y`
 - `pip install cptac`

If you are unfamiliar with miniconda and do not have it installed, reference their documentation here: https://www.anaconda.com/docs/getting-started/miniconda/install

Throughout this repo we will be using jupyter notebooks to run everything.  This means the first time you run the notebooks you will have to select the kernel which corresponds to the conda environment called `eris`.  If you are unfamiliar with jupyter notebooks, you can find their documentation here: https://docs.jupyter.org/en/latest

## Overview
This repo is split into two groups - TCGA and CPTAC which should closely mirror each other in how they work and figures produced.  The main difference is that TCGA has enough data to where it cannot be stored all on github.  Let's start with TCGA.

# TCGA

## Step 1: Acquire Data

We have saved a zip file with the data we are using for TCGA to the following google drive folder: https://drive.google.com/file/d/1WADpFgwA9jiEaA3gQkHLKLUfY_D7KjqI/view?usp=sharing

Once you download the expression_data.zip file, save it to tcga/data.  If you have opted for this method you can skip to step 2.

Alternatively, we have put together a pipeline to pull the data although we would strongly discourage running this, as it uses the gdc client which limits download rates and our testing was limited to the mac distribution of the gdc-client tool.  If you do decide to use this tool it should take around 20-30 hours to complete.  At which point you will have to zip the file and name it `expression_data.zip` and save it to tcga/data to be used within our notebooks.  To run it on mac, go to the tcga folder and run the following: 
 - `python download_data.py`

The first time you run this, your firewall/malware protection may block it.  If this occurs, close out of your terminal and stop it from running.  To allow this to run go to your system settings and open the privacy & security tab.  Scroll down to security where it says `"gdc-client-mac" was blocked to protect your Mac` and click Allow Anyway.  Now rerun the command, click open anyway, and it should work.

If you want to run it on ubuntu we have also downloaded the ubuntu distribution and to use it you will need to edit the `download_data.sh` file -- You would need to replace 
 - `echo "$@" | xargs -n 1 -P $PARALLEL_DOWNLOADS ./gdc_distributions/gdc-client-mac download -d ./data` with
 - `echo "$@" | xargs -n 1 -P $PARALLEL_DOWNLOADS ./gdc_distributions/gdc-client-ubuntu download -d ./data`

Now, navigate to the parent directory and run the following:
 - `python download_data.py`

## Step 2: Data Filtering
This processing is completed in notebook `00_data_filtering.ipynb`
 - You shouldn't have to adjust anything assuming you have the zipped data stored in the correct location (as explained in step 1)
 - Select the eris conda environment as the kernel for the notebook and run all cells
 - This notebook takes in expression_data.zip, unzips it, reads the dataframe within, filters for the genes of interest as defined in genes.json, scores the different markers, and then saves the resulting dataframe as `tcga/data/processed_data.tsv`


## Step 3: Creating Distribution Figure
This figure generation is completed in notebook `01_distribution.ipynb`

This figure shows a distribution of the number of patients included in our study across all cancer types. If you want the files to be in a specific folder then you can use the second cell to choose a file name and destination. 

Run all of the cells without customizing to save "Demographics" within the "Figures" folder. 

## Step 4: Creating Figure 1
This figure generation is completed in notebook `02_figure_1.ipynb`

The figure shows a distribution of scores across chosen traits and the overall score. Use the first cell to customize the file names and locations. 

Run all cells without updating them to save "figure_1.png" to the "figures" folder. 

## Step 5: Creating Figure 2
This figure generation is completed in notebook `03_figure_2.ipynb`

Figure 2 is a plot that shows the percent of patients that would be likely to respond very well, and just well to ASMase therapy. The figure displays the percent of patients that score above the 50th percentile across all cancer types with a grey bar. Patients who score above the 80th percentile across all cancer types are contained within the blue bar. Use the second cell of the notebook to customize file name and location. 

Run all cells without updating them to save "figure_2.png"  to the "figures" folder.

# CPTAC

## Step 1: Acquire/Process Data
In `00_data_filtering.ipynb`, run each cell sequentially. This file utilizes the `cptac` package  (https://github.com/PayneLab/cptac) to download and process proteomics and transcriptomics data from the National Cancer Institute's CPTAC program. Some cells may require a few minutes to run. Ultimately, this file will output two files (`proteomics_data.tsv` and `transcriptomics_data.tsv`) to the `/data` folder to be used for downstream analysis and figure generation.

## Step 2: Distribution
In `01_distribution.ipynb`, run each cell sequentially. This file will save two figures (`distribution_proteomics.png` and `distribution_transcriptomics.png`) in the `/figures` folder.
These figures show the distribution of patients across all cancer types for both the proteomics and transcriptomics data respectively.

## Step 3: Figure 1
In `02_figure_1.ipynb`, run each cell sequentially. This file will save two figures (`figure_1_proteomics.png` and `figure_1_transcriptomics.png`) in the `/figures` folder.
These figures show the distribution of scores across chosen traits as well as the overall score.

## Step 4: Figure 2
In `03_figure_2.ipynb`, run each cell sequentially. This file will save two figures (`figure_2_proteomics.png` and `figure_2_transcriptomics.png`) in the `/figures` folder.
These figures show the percent of candidates acrosss cancer types. They display the percent of patients that score above the 50th percentile across all cancer types with a grey bar. Patients who score above the 80th percentile across all cancer types are contained within the blue bar.
