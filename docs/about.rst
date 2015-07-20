1. About
========
SHIVA (*Spam Honeypot with Intelligent Virtual Analyzer*), is a spampot(i.e. a spam honeypot) written in Python2.7, built on top of Lamson framework. SHIVA is an open-source, high interaction honeypot, and is released under GNU General Public Licence version 3. SHIVA provides capabilities of collecting and analyzing all spam thrown at it. Analysis of data captured can be used to get information of phishing attacks, scamming campaigns, malware campaigns, spam botnets, etc. SHIVA uses MySQL for storing information. Below are some of the stand out features of SHIVA:

1.1 Features
--------------
* **Controlled Relay:** SHIVA provides the ability to control the relay part completely. User can enable/disable and set the number of spam to be relayed, in the configuration file.Here is the required section.

* **Open Source:** SHIVA is open source, therefore it is very easy to extend the capabilities. For example, one could easily write a simple module to send the attachments to VirusTotal for further analysis.

* **Identifying Unique Spam:** SHIVA uses fuzzy hashingtechnique to distinguish between new and already seen spam. This makes it possible to analyze millions of spam and still keeping the database size in check.Python implementation of ssdeep is used.

* **Extracting Information from Spam:** Every spam received passes through the mail parser. SHIVA's mail parser is written to extract all the information that is important. Mail parser extracts source IP, spam's various parts like -to, from, header, subject, body, URLs, attachments, etc. This information is then saved in database, if user has opted for setting up database storage.

* **Supports Authentication:** SHIVA provides more control over the SMTP receiver by adding SMTP authentication feature to it. This way, a user can restrict the access to his SMTP server bysetting up credentials.

* **Hpfeeds sharing:** SHIVA also makes sharing the analyzed data easy by adding the Hpfeeds/Hpfriends support. Hpfriends is the social data-sharing platform by The Honeynet Project. Again, Hpfeeds/ Hpfriends can be configured by setting up related options in configuration file.
