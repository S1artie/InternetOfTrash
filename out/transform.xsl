<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" id="xhtmltransform" version="1.0">
<xsl:output method="html" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" />
<xsl:template match="iot">
  <html>
  	<head>
      <title>
        <xsl:text>Internet Of Trash</xsl:text>
      </title>
      <style type="text/css">
        html { width: 100%; height: 100%; }
      	body { font-family: Calibri, Arial, sans-serif; font-size: 16pt; color: #fff; margin: 0px; display: block; border-collapse: collapse; width: 100%; height: 100%; }
      	#outer { margin: 0px; display: block; width: 980px; height: 575px; position: absolute; background-color: #000; }
      	#timestamp { position: absolute; right: 4px; top: 4px; font-size: 14px; }
      	.header { padding-bottom: 16px; }
      	.title { font-weight: bold; font-size: 26px; height: 30px; border-bottom: 1px solid #fff; margin: 10px; }
      	.content { margin-left: 20px; margin-right: 20px; }
      	.temperatures { height: 100px; }
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
      </style>
    </head>
    <body>
      <div id="outer">
          <div id="timestamp">
          		<xsl:text>aktualisiert: </xsl:text>
          		<xsl:value-of select="@timestamp" />
          	</div>
          <div class="header">
          	<div class="title">
                <xsl:text>Temperaturen</xsl:text>
          	</div>
          </div>
          <div class="content temperatures">
            <xsl:apply-templates select="temperatures" />
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
    <div class="temperature">
        <div class="label"><xsl:value-of select="concat('Tagestiefsttemperatur ', @forecastTarget)" /></div>
        <div class="value monospace"><xsl:value-of select="@forecastLow" /></div>
        <div class="unit monospace">°C</div>
    </div>
    <div class="temperature">
        <div class="label">Getränkekühltruhe aktuell</div>
        <div class="value monospace"><xsl:value-of select="@cooler" /></div>
        <div class="unit monospace">°C</div>
    </div>
    <div class="temperature">
        <div class="label"><xsl:value-of select="concat('Tageshöchsttemperatur ', @forecastTarget)" /></div>
        <div class="value monospace"><xsl:value-of select="@forecastHigh" /></div>
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
				<xsl:if test="@nextPickupDays > 2">
					<xsl:value-of select="concat('wird in ', @nextPickupDays, ' Tagen abgeholt')" />
				</xsl:if>
                <xsl:if test="@nextPickupDays = 1">
					<xsl:value-of select="concat('wird morgen abgeholt')" />
				</xsl:if>
				<xsl:if test="@nextPickupDays = 0">
					<xsl:value-of select="concat('wird heute abgeholt')" />
				</xsl:if>
            </div>            
        </div>
    </div>
</xsl:template>
</xsl:stylesheet>
