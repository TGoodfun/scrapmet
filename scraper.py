 ###
 
 csv     = require 'csv-string'
-util    = require 'util'
 http    = require 'http'
 async   = require 'async'
 jsdom   = require 'jsdom'
 @@ -28,35 +27,26 @@ selectors =
     date:    '.review_stats .review_critic .date'
 
 # scrape
-# page (number)     the page number to scrape
 # platform (string) the platform to scrape
-# letter (string)   the leading title character to scrape
-scrape = (page, platform, letter, done) ->
+# page (number)     the page number to scrape
+scrape = (platform, page = 0) ->
   jsdom.env
-    html: "http://www.metacritic.com/browse/games/title/#{platform}/#{letter}?page=#{page}"
+    html: "http://www.metacritic.com/browse/games/title/#{platform}?page=#{page}"
     done: (errors, window) ->
       links = window.document.querySelectorAll '.product_condensed > ol.list_products > li a'
       if links.length
-        async.series
-          links: (callback) ->
-            for link in links
-              scrapegame link.getAttribute('href'), callback
-          (err, results) ->
-            scrape ++page, platform, letter, done
-      else
-        done()
+        iterator = (link, cb) ->
+          scrapegame link.getAttribute('href'), cb
 
-letters = [ '' ]
-
-for charCode in [65..90]
-  letter = String.fromCharCode(charCode).toLowerCase()
-  letters.push letter
+        async.eachLimit links, 1, iterator, (err) ->
+          scrape platform, ++page
+      return
+  return
 
-async.eachLimit letters, 4, (letter, done) ->
-  scrape 0, 'xbox360', letter, done
+scrape 'xbox360'
 
-scrapegame = (url, done) ->
-  async.parallel
+scrapegame = (url, complete) ->
+  async.series
     critic: (callback) ->
       jsdom.env
         html: "http://www.metacritic.com#{url}/critic-reviews"
 @@ -75,7 +65,10 @@ scrapegame = (url, done) ->
           else
             scrapereview window.document, 'userreview', callback
     (err, results) ->
-      done(err, results)
+      complete()
+      return
+
+  return
 
 scrapereview = (document, reviewtype, callback) ->
   # catch error pages
 @@ -83,6 +76,7 @@ scrapereview = (document, reviewtype, callback) ->
   #  instead, errors are 200 OK responses, so we search for error module content
   #  in the response body
   if document.querySelector '.errorcode_module'
+    callback(null, 0)
     return
 
   type     = if reviewtype is 'criticreview' then 'Expert' else 'User'
 @@ -98,4 +92,5 @@ scrapereview = (document, reviewtype, callback) ->
     console.log csv.stringify([ title, platform, type, date, score, source ]).trim()
 
   callback(null, reviews.length)
+
   return
