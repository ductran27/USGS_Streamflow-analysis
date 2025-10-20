# How to Set Up Automatic Daily Commits

This guide explains how to get your streamflow analysis running automatically every day.

## Step 1: Install Dependencies

First, make sure you have Python installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

## Step 2: Test It Locally

Run the script once to make sure everything works:

```bash
python main.py
```

You should see output showing data being fetched and analyzed. Check the `plots/` and `results/` folders for the generated files.

## Step 3: Create GitHub Repository

1. Go to github.com and sign in
2. Click the "+" button in top right, select "New repository"
3. Name it something like "streamflow-analysis" or "usgs-water-monitoring"
4. Keep it PUBLIC (important for unlimited GitHub Actions minutes)
5. Do NOT initialize with README, .gitignore, or license
6. Click "Create repository"

## Step 4: Push Your Code

In the hydro-automation folder, run these commands:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Make your first commit
git commit -m "Initial commit"

# Connect to GitHub (replace YOUR_USERNAME and YOUR_REPO with your details)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 5: Enable Automatic Daily Updates

Once your code is on GitHub, the automation will start working automatically. Here's what happens:

1. Every day at 9:00 AM UTC, GitHub Actions will run your script
2. It fetches new USGS data
3. Performs analysis
4. Generates updated plots
5. Commits the new results to your repository

That's it! No additional setup needed.

## Verify It's Working

To check if automation is running:

1. Go to your repository on GitHub
2. Click the "Actions" tab
3. You'll see the workflow runs listed there
4. Each successful run will create a new commit in your repository

## Manual Trigger (Optional)

If you want to run it immediately instead of waiting for the scheduled time:

1. Go to repository on GitHub
2. Click "Actions" tab
3. Select "Daily Hydrology Data Update" workflow
4. Click "Run workflow" button
5. Select branch (main) and click green "Run workflow" button

The script will run immediately and you can watch the progress in real-time.

## Customization

To monitor different USGS stations, edit `config.yaml`:

```yaml
data_sources:
  usgs_sites:
    - "01646500"  # Replace with your site codes
    - "01491000"  # You can add multiple sites
```

Find USGS site codes at: https://waterdata.usgs.gov/nwis

To change the schedule, edit `.github/workflows/daily-update.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Hour and minute in UTC
```

## Troubleshooting

**Nothing happening after push:**
- Check if Actions are enabled: Repository Settings > Actions > General
- Make sure the workflow file is in `.github/workflows/` folder

**Workflow fails:**
- Click on the failed run in Actions tab to see error details
- Most common issue: missing dependencies or invalid site codes

**No commits appearing:**
- Workflow only commits if there are changes (new data, updated plots)
- Check the Actions tab to see if the workflow is running successfully

## What Gets Committed

The automation commits:
- Updated analysis results (JSON files in `results/`)
- New visualizations (PNG files in `plots/`)
- Data summaries

Raw data files in `data/` are NOT committed (they're in .gitignore).

## Important Notes

- This uses public USGS data (no API keys needed)
- GitHub Actions is free for public repositories
- Each run takes about 1-2 minutes
- Your contribution graph will show daily activity
- All analysis is real scientific work with actual data

## That's All

Once set up, the system runs completely automatically. You'll see daily commits appearing on your GitHub profile showing your ongoing data analysis work.
