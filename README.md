# DGS Express Knowledgebase

A single-page reference built from the DGS Express Knowledgebase slide deck:
88 entries covering actions, concepts, screens, cuts, offenses and ball screen
coverages, with the original court diagrams.

These slides were created by Coach Chang of Elmhurst Basketball. Revised for by Coach Epps.

## What is in here

```
index.html      the whole site, one file
img/            107 court diagrams plus the program logo
.nojekyll       tells GitHub Pages to serve the files as they are
```

No build step, no dependencies. Open `index.html` locally and it works.

## Putting it on GitHub Pages

1. Create a repository, for example `dgs-express-knowledgebase`.
2. Drop these files in the root of the repository and push:

   ```
   git init
   git add .
   git commit -m "DGS Express Knowledgebase"
   git branch -M main
   git remote add origin https://github.com/<your-account>/dgs-express-knowledgebase.git
   git push -u origin main
   ```

3. In the repository, go to **Settings → Pages**, set **Source** to
   "Deploy from a branch", branch `main`, folder `/ (root)`, and save.
4. After a minute the site is live at
   `https://<your-account>.github.io/dgs-express-knowledgebase/`.

To use a custom address such as `knowledgebase.dgsexpress.org`, add a file named
`CNAME` containing that hostname, then point a CNAME DNS record at
`<your-account>.github.io`.

## Updating it

Everything lives in `index.html`. Edit the text there and push again; Pages
redeploys on its own. To add a diagram, drop the image in `img/` and reference
it the same way the existing figures do.

## Notes

- Every entry has its own anchor, so you can link straight to one:
  `.../#hard-hedge`, `.../#ghost-screen`, `.../#pistol-offense`.
- The search box filters entries as you type. Browser find (Ctrl+F or Cmd+F)
  searches the full text of all 88 entries at once.
- The layout is responsive and prints cleanly, so a coach can print one entry
  without the navigation.
