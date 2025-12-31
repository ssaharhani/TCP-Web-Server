# Project Specifications: TCP Web Server

Using socket programming, this task involves implementing a simple but complete web server that listens on **port 5012**. The server is designed to handle multiple file types, provide localized content (English/Arabic), and manage specific HTTP status codes.

## 1. Webpage Requirements

### a. Main English Webpage (`main_en.html`)
The primary interface must include:
* **Browser Tab:** Displays "ENCS3320-T1243".
* **Header:** Title "Welcome to Computer Networks Webserver" at the top.
* **Team Section:** * Member photos (`.png`), names, and IDs.
    * Organized in a table-like structure with separate boxes for each member.
    * Brief descriptions (projects, skills, hobbies).
* **Gaza Awareness Section:** * Informative overview of the suffering in Gaza (war, loss, displacement, and food/water scarcity).
    * Formatted with structured paragraphs, headings, bold/italic text, and `.jpg` images.
    * Contains both ordered and unordered lists.
* **Event Search Form:** * An input box for users to request details about specific war events.
    * If the keyword matches a local file (`event_details.html`), the server serves that file.
    * **307 Temporary Redirects:** If the topic is unavailable, redirect based on input type:
        * **Text:** Redirect to [Al Jazeera Search](https://www.aljazeera.com/).
        * **Images:** Redirect to [Google Images Search](https://www.google.com/).
        * **Videos:** Redirect to [YouTube Search](https://www.youtube.com/).
* **External Links:** * [Textbook Website](https://gaia.cs.umass.edu/kurose_ross/index.php)
    * [Ritaj Website](https://ritaj.birzeit.edu/)
* **Styling:** A separate **CSS file** must be used to style the page attractively.

### b. Arabic Versions
* Provide `main_ar.html` and `event_details_ar.html` as the Arabic counterparts to the English pages.

---

## 2. Server Functionality

When an HTTP request is received, the server must:
1.  **Log Details:** Print the full HTTP request details to the terminal.
2.  **Generate Response:** Send the requested content with the correct `Content-Type` header:
    * `text/html` for HTML files.
    * `text/css` for CSS files.
    * `image/png` or `image/jpeg` for images.
    * `video/mp4` for videos.

---

## 3. Routing and Error Handling

### Default Routes
The server should serve the main pages based on the following paths:
| Path / URL | Served File |
| :--- | :--- |
| `/`, `/en`, `/index.html`, `/main_en.html` | `main_en.html` |
| `/ar`, `/main_ar.html` | `main_ar.html` |

### 404 Not Found
If a client requests an invalid URL, the server must return a custom error page:
* **Status Line:** `HTTP/1.1 404 Not Found`
* **Browser Tab:** "Error 404"
* **Body Content:** * "The file is not found" (displayed in **red text**).
    * Display of the client’s **IP address** and **port number**.

---
> **NOTE:** This project was done as part of the Computer Networks course in Birzeit University, T1243.

> **Project Info** > ENCS3320
