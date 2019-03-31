1. Open Git Bash -> Type npm install (only needed first time) then Type: npm run dev
   This will bring up a development server that its index.html file will be served at http://localhost:8080
2. The main file for edit is "index.ejs" which is like the index.html.
   The main JS file is app/timeMap.js
   The main CSS file is assets/styles/_custom.scss
3. As long as "npm run dev" is running, each change you make will trigger a refresh on localhost:8080 right away.
4. When you're done editing the code, you need to build it so you have static files for the website:
a. Go to the Git bash -> press ctrl+c -> Type: npm run build
b. Once done, a "dist" folder is created under 