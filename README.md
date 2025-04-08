# Setup
To get started using this repo you will need to use our yaml file to create a conda environment with the necessary packages.  To do this, navigate to this repo's parent directory and run the following:

 - `conda env create -f environment.yml`

 - `conda activate eris `

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

If you want to run it on ubuntu we have also downloaded the ubuntu distribution and to use it you will need to edit the `download_data.sh` file -- You would need to replace 
 - `echo "$@" | xargs -n 1 -P $PARALLEL_DOWNLOADS ./gdc_distributions/gdc-client-mac download -d ./data` with
 - `echo "$@" | xargs -n 1 -P $PARALLEL_DOWNLOADS ./gdc_distributions/gdc-client-ubuntu download -d ./data`

Now, navigate to the parent directory and run the following:
 - `python download_data.py`

## Step 2: Data Filtering
This process is completed in notebook `00_data_filtering.ipynb`


Step 3: Creating Demogrphic Distribution Figure
This figure shows a distribution of the number of patients included in our study across all cancer types. If you want the files to be in a specific folder then you can use the second cell to choose a file name and destination. 
Run all of the cells without customizing to save "Demographics" within the "Figures" folder. 

Step 4: Creating Figure 1: a plot of the distribution of individual trait scores and an overall score.
The figure shows a distribution of scores across chosen traits and the overall score. Use the first cell to customize the file names and locations. 
Run all cells without updating them to save "Figure 1" to the "Figures" folder. 

Step 5: Creating Figure 2: a plot that shows the percent of patients that would be likely to respond very well, and just well to ASMase therapy. 
The figure displays the percent of patients that score above the 50th percentile across all cancer types with a grey bar. Patients who score above the 80th percentile across all cancer types are contained within the blue bar. Use the second cell of the notebook to customize file name and location. 
Run all cells without updating them to save "Figure 2"  to the "Figures" folder. 
