<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" id="xhtmltransform" version="1.0">
<xsl:output method="html" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" />
<xsl:template match="iot">
  <html>
  	<head>
      <title>
        <xsl:text>Internet Of Trash</xsl:text>
      </title>
      <link href='https://fonts.googleapis.com/css?family=Orbitron' rel='stylesheet' type='text/css'></link>
      <style type="text/css">
        html { width: 100%; height: 100%; }
      	body { font-family: Calibri, Arial, sans-serif; font-size: 16pt; color: #fff; margin: 0px; display: block; border-collapse: collapse; width: 100%; height: 100%; }
      	#outer { margin: 0px; padding-top: 15px; display: block; width: 980px; height: 560px; position: absolute; background-color: #000; }
      	#timestamp { position: absolute; right: 4px; bottom: 4px; font-size: 14px; }
      	.header { padding-bottom: 16px; }
      	.title { font-weight: bold; font-size: 26px; height: 30px; border-bottom: 1px solid #fff; margin: 10px; }
      	.content { margin-left: 20px; margin-right: 20px; }
      	.temperatures { height: 90px; }
      	.temperature { display: block; float: left; width: calc(50% - 50px); padding-left: 10px; padding-right: 40px; margin-bottom: 10px; }
      	.temperatures:last-child { float: none !important; }
      	.temperature .label { width: 74%; float: left; }
      	.temperature .value { width: calc(18% - 6px); float: left; text-align: right; padding-right: 6px; }
      	.temperature .unit { width: 8%; float: right; }
      	.temperature .monospace { font-family: "DejaVu Sans Mono", Menlo, Consolas, "Liberation Mono", Monaco, "Lucida Console", monospace  }
      	.trashcan { height: 50px; margin-bottom: 20px; padding: 5px; border: 1px dashed #555; }
      	.trashicon { width: 34px; height: 50px; float: left; }
      	.trashicon_1 { background-image: url("data:image/png;base64,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"); }
      	.trashicon_2 { background-image: url("data:image/png;base64,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"); }
      	.trashicon_3 { background-image: url("data:image/png;base64,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"); }
      	.trashicon_4 { background-image: url("data:image/png;base64,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"); }
      	.trashcan .name { margin-left: 10px; margin-top: 12px; width: 240px; font-weight: bold; float: left; }
      	.trashcan .param { height: 50px; float: left; margin-top: 4px; }
      	.trashcan .param .status { float: none !important; }
      	.trashcan .param .paramName { font-size: 12px; color: #fff; margin-bottom: 3px; }
      	.trashcan .location { width: 240px; }
      	.trashcan .pickupToday { font-weight: bold; color: #DB0000; animation: 2s steps(1, end) infinite alert;  }
      	.trashcan .pickupTomorrow { font-weight: bold; color: #DB0000; animation: 4s infinite softAlert;  }
      	.trashcan .pickupTomorrowAlert { font-weight: bold; color: #DB0000; animation: 2s steps(1, end) infinite alert; }
        @keyframes alert {
      	    0% { color: #CC0000; }
      	    50% { color: #FFFFFF; }
      	    100% { color: #CC0000; }
      	}
      	@keyframes softAlert {
      	    0% { color: #CC0000; }
      	    50% { color: #FF0000; }
      	    100% { color: #CC0000; }
      	}
        #clockarea { position: absolute; top: 8px; right: 4px; color: #FFFF00; font-family: digital-7regular; letter-spacing: 7px; font-weight: bold; font-size: 36pt; }
        #clock { position: absolute; right: 0px; top: 0px; z-index: 2; }
        #clockbackground { position: absolute; right: 0px; top: 0px; z-index: 1; color: #222; }
        @font-face {
            font-family: 'digital-7regular';
            font-weight: normal;
            font-style: normal;
            src: url(data:application/font-woff2;charset=utf-8;base64,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) format('woff2'); 
        }
        #labelbutton { width: 36px; height: 36px; position: absolute; top: 10px; right: 280px; z-index: 20; background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAYAAADhAJiYAAAEtmlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgZXhpZjpQaXhlbFhEaW1lbnNpb249IjM2IgogICBleGlmOlBpeGVsWURpbWVuc2lvbj0iMzYiCiAgIGV4aWY6Q29sb3JTcGFjZT0iNjU1MzUiCiAgIHRpZmY6SW1hZ2VXaWR0aD0iMzYiCiAgIHRpZmY6SW1hZ2VMZW5ndGg9IjM2IgogICB0aWZmOlJlc29sdXRpb25Vbml0PSIyIgogICB0aWZmOlhSZXNvbHV0aW9uPSI5Ni8xIgogICB0aWZmOllSZXNvbHV0aW9uPSI5Ni8xIgogICBwaG90b3Nob3A6Q29sb3JNb2RlPSIzIgogICBwaG90b3Nob3A6SUNDUHJvZmlsZT0iR2VuZXJpYyBSR0IgUHJvZmlsZSIKICAgeG1wOk1vZGlmeURhdGU9IjIw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"); }
        #labelprinter { position: absolute; top: 60px; left: 100px; z-index: 10; width: 780px; height: 400px; background: rgba(0,0,0,0.9); border: 2px solid #fff; border-radius: 20px 10px; box-shadow: 0px 0px 0px 200px rgba(0,0,0,0.7);  }
        #printlines { padding-top: 10px; }
        .printline { display: grid; grid-template-columns: 100px auto; padding-left: 10px; padding-right: 10px; padding-bottom: 10px; }
        .printline div { grid-column: 1; align-self: center; }
        .printline input { grid-column: 2; font-size: 20px; text-align: center; }
        #printbuttons { display: flex; flex-direction: row; height: 40px; justify-content: center; }
        #printbuttons button { width: 40px; height: 40px; margin-left: 5px; margin-right: 5px; border: 2px solid white; border-radius: 15px 5px; background-color: black; color: white; }
        #printbuttonx1 { width: 200px !important }
        .printtemplates { display: flex; flex-wrap: wrap; padding-left: 10px; padding-right: 10px; padding-top: 20px; }
        .printtemplates button { margin: 3px; font-size: 15px; padding: 8px; border: 1px solid white; border-radius: 10px 3px; background-color: black; color: white; opacity: 0.6; }
      </style>
      <script>
<![CDATA[
    function startTime(){
        var today = new Date();
        var h = today.getHours();
        var m = today.getMinutes();
        var s = today.getSeconds();
        var ms = today.getMilliseconds();
        var dots = (ms < 500 ? ":" : "<span style=\"visibility: hidden;\">:</span>");
        var time = fill(h) + dots + fill(m) + dots + fill(s);
        document.getElementById('clock').innerHTML = time;
        var t = setTimeout(startTime, 500);   
    }
    function fill(i) {
        if (i < 10) {
            return "0" + i;
        }
        return i;
    }

    function toggleLabelPrinter() {
        var div = document.getElementById('labelprinter');
        if (div.style.display == "block") {
            div.style.display = "none";
        } else {
            var dateFormat = {day: 'numeric', year: 'numeric', month: 'short'};
            document.querySelector('#printline1 input').value = "";
            document.querySelector('#printline2 input').value = new Date().toLocaleDateString('de-DE', dateFormat);
            
            var templateData = [
                "Tomatensauce",
                "Tomatensuppe",
                "Bolognese",
                "Pizzasauce",
                "Gulasch",
                "Chili con carne",
                "Thai-Curry",
                "Käsespätzle",
                "Spätzlepfanne",
                "Hähnchenbrust",
                "Erbsensuppe",
                "Linseneintopf",
                "Pesto",
                "Rouladen",
                "Reis",
                "Kekse",
                "Wrap-Sauce",
                "Marinade",
                "Asiastuff",
            ]
            document.getElementById('printtemplates1').innerHTML = templateData.sort().map(item => `<button onclick="setLabelLine1('${item}')">${item}</button>`).join('');
            
            var timestamp = new Date().getTime();
            var dayOffset = 24*60*60*1000;
            templateData = [
                new Date(timestamp - dayOffset * 1).toLocaleDateString('de-DE', dateFormat),
                new Date(timestamp - dayOffset * 2).toLocaleDateString('de-DE', dateFormat),
                new Date(timestamp - dayOffset * 3).toLocaleDateString('de-DE', dateFormat),
                new Date(timestamp - dayOffset * 4).toLocaleDateString('de-DE', dateFormat),
                new Date(timestamp - dayOffset * 5).toLocaleDateString('de-DE', dateFormat),
                new Date(timestamp - dayOffset * 6).toLocaleDateString('de-DE', dateFormat),
                "",
            ]
            document.getElementById('printtemplates2').innerHTML = templateData.map(item => `<button onclick="setLabelLine2('${item}')">${item}</button>`).join('');

            div.style.display = "block";
            disableInterferingLight();
        }
    }

    function setLabelLine1(text) {
        document.querySelector('#printline1 input').value = text;
    }
    function setLabelLine2(text) {
        document.querySelector('#printline2 input').value = text;
    }

    function printLabel(count) {
        var url = "/cgi-bin/labelprinter/labelprinter.py?firstLine=" + encodeURIComponent(document.querySelector('#printline1 input').value) + "&secondLine=" + encodeURIComponent(document.querySelector('#printline2 input').value) + "&copies=" + count;
        const http = new XMLHttpRequest();
        http.open("GET", url);
        http.send();

        toggleLabelPrinter();
    }

    function disableInterferingLight() {
        const http = new XMLHttpRequest();
        http.open("GET", "/cgi-bin/labelprinter/disableInterferingLight.py");
        http.send();
    }

    window.setInterval(function () {
        if(document.getElementById('labelprinter').style.display != "block") {
            window.location.reload();
        }
    }, 120000);
]]>
    </script>
    </head>
    <body onload="startTime()" onclick="disableInterferingLight()">
      <div id="outer">
          <div id="timestamp">
          		<xsl:text>aktualisiert: </xsl:text>
          		<xsl:value-of select="@timestamp" />
          </div>
          <div id="clockarea">
              <div id="clock"></div>
              <div id="clockbackground">88:88:88</div>
          </div>
          <div id="labelbutton" onclick="toggleLabelPrinter()">
          </div>
          <div id="labelprinter" style="display: none">
            <div id="printlines">
                <div id="printline1" class="printline"><div>Zeile 1</div><input type="text"/></div>
                <div id="printline2" class="printline"><div>Zeile 2</div><input type="text"/></div>
            </div>
            <div id="printbuttons">
                <button id="printbuttonx1" onclick="printLabel(1)">Label drucken</button>
                <button id="printbuttonx2" onclick="printLabel(2)">x2</button>
                <button id="printbuttonx3" onclick="printLabel(3)">x3</button>
                <button id="printbuttonx4" onclick="printLabel(4)">x4</button>
                <button id="printbuttonx5" onclick="printLabel(5)">x5</button>
            </div>
            <div id="printtemplates1" class="printtemplates">
            </div> 
            <div id="printtemplates2" class="printtemplates">
            </div>            
          </div>
          <div class="header">
          	<div class="title">
                <xsl:text></xsl:text>
          	</div>
          </div>
          <div class="content temperatures">
            <!--<xsl:apply-templates select="temperatures" />-->
          </div>
          <div class="header">
          	<div class="title">
          		<xsl:text>Mülltonnen</xsl:text>
          	</div>
          </div>
          <div class="content trashcans">
          	<xsl:for-each select="trashcan">
    		  <xsl:apply-templates select="." />
    		</xsl:for-each>
          </div>
      </div>
	</body>
  </html>
</xsl:template>
<xsl:template match="temperatures">
    <div class="temperature">
        <div class="label">Außentemperatur aktuell</div>
        <div class="value monospace"><xsl:value-of select="@outside" /></div>
        <div class="unit monospace">°C</div>
    </div>
</xsl:template>
<xsl:template match="trashcan">
    <div class="trashcan">
        <div>
            <xsl:attribute name="class">
				<xsl:value-of select="concat('trashicon trashicon_', @type)" />				
			</xsl:attribute>
        </div>
        <div class="name"><xsl:value-of select="@name" /></div>
        <div class="param location">
            <div class="paramName">Standort</div>
            <div class="paramValue"><xsl:value-of select="@location" /></div>            
        </div>
        <div class="param status">
            <div class="paramName">Status</div>
            <div class="paramValue">
                <xsl:attribute name="class"><xsl:value-of select="concat('paramValue ', @alert)" /></xsl:attribute>
				<xsl:if test="@nextPickupDays >= 2">
					<xsl:value-of select="concat('wird in ', @nextPickupDays, ' Tagen abgeholt')" />
				</xsl:if>
                <xsl:if test="@nextPickupDays = 1">
					wird morgen abgeholt
				</xsl:if>
				<xsl:if test="@nextPickupDays = 0 and @alert != ''">
					wird heute abgeholt
				</xsl:if>
                <xsl:if test="@nextPickupDays = 0 and @alert = ''">
                    wurde heute abgeholt
                </xsl:if>
            </div>            
        </div>
    </div>
</xsl:template>
</xsl:stylesheet>
