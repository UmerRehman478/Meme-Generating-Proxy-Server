# 🐼 Meme-Generating Proxy Server

This project is a fun proxy server that changes some images on websites into memes. When someone visits a regular (HTTP only) website through this server, it randomly replaces some of the images with funny ones from your own meme folder.

---

## 🧠 What It Does

- It works like a middleman between your web browser and websites.
- It looks at what images a site is loading, and randomly changes 50% of them to memes.
- If someone visits a specific website (like `http://google.ca`), it shows a surprise meme page instead of the usual one.

---

## 🎯 Features

- **Handles Multiple Users:** Can work with many browsers at once using threads.
- **Replaces Images:** Swaps half of the normal images on a page with random memes from your collection.
- **Custom Meme Folder:** You control which memes are used by adding them to a local folder.
- **Easter Egg:** A custom surprise is shown when visiting a specific site.
- **Only for HTTP Sites:** HTTPS sites won’t work (e.g., `http://httpbin.org/` works, `https://example.com` does not).

---

## 📁 Folder Setup

```
project-folder/
├── memes/             # Folder with at least 15 meme images (e.g., .jpg, .png)
├── proxy_server.py    # The main Python script
├── README.md          # This file
```

Make sure the `memes/` folder contains meme images before you run the server.

---

## 🛠 How to Run

1. **Install Python 3**  
   Make sure Python 3 is installed on your machine. You can download it from https://www.python.org.

2. **Run the Server**

   In your terminal, go to your project folder and type:
   ```bash
   python proxy_server.py
   ```

3. **Configure Your Browser**

   In your browser settings:
   - Set the proxy to `127.0.0.1`
   - Use the port number your server is listening on (default might be `8080`)

   Example browser proxy settings:
   - HTTP Proxy: `127.0.0.1`
   - Port: `8080`

4. **Visit an HTTP Website**

   Go to a website like:
   ```
   http://httpbin.org/
   ```
   You should see some of the images replaced with memes.

5. **Try the Easter Egg**

   Go to:
   ```
   http://google.ca
   ```
   You’ll see a custom meme page with surprises.

---

## ❗ Notes

- This only works with HTTP websites (not HTTPS).
- If your browser doesn’t show any memes, check that:
  - The `memes/` folder has images.
  - The server is running and listening on the correct port.
  - The browser proxy settings are correct.

---

## 💡 Example Memes

Make sure your `memes/` folder includes image files like:
```
- panda1.jpg
- grumpycat.png
- funny_meme.gif
- etc.
```

---

## 🔧 Troubleshooting

- **Problem**: Nothing loads in the browser  
  **Fix**: Check if the server is running, and proxy settings are correct.

- **Problem**: HTTPS websites don’t work  
  **Fix**: This server only supports HTTP.

- **Problem**: No memes appear  
  **Fix**: Make sure there are images in your `memes/` folder and they're in supported formats like `.jpg`, `.png`, or `.gif`.

---

Enjoy watching the web turn into meme-land with Mochi the panda! 🐼🎉
