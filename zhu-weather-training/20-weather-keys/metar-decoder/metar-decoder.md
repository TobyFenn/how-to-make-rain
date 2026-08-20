---
title: "METAR Decoder"
page_title: "How to Decode METAR, TAF, and pilot reports"
section: "Weather Keys"
source_url: "https://met.nps.edu/~bcreasey/mr3222/files/helpful/DecodeMETAR-TAF.html"
captured: "2026-08-19 06:00 UTC"
via: "live"
kind: "html"
pdf: "metar-decoder.pdf"
original: "source/original.html"
---

# METAR Decoder

> Source: <https://met.nps.edu/~bcreasey/mr3222/files/helpful/DecodeMETAR-TAF.html>  
> Section: Weather Keys  
> Captured: 2026-08-19 06:00 UTC  
> PDF: [metar-decoder.pdf](metar-decoder.pdf) · Original HTML: [source/original.html](source/original.html)

---

## **How to Decode METAR, TAF, and pilot reports.**

**A METAR is a codified observation message
indicating an airfield weather conditions observed at a given time.

Such a message is established every hour.

A SPECI message is identical to a METAR but is
established punctually instead of regularly. It is a special observation
message highlighting any significant change since the last METAR or
SPECI was issued.

A TAF is a terminal forcast.  It is issued
every few hours, and is updated if necessary sooner.**

### Aviation Routine Weather Report (METAR)

 

Example:

|  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| METAR | KRNO | 210056Z | 05012KT | 10SM | -SN | BKN050 | 02/M08 | A3016 | RMK AO2 SLP228 | T00221083 |
| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |

 

1.    
Message Type

·        
METAR: routine weather report

·        
SPECI: special weather report, triggered by a weather change

·        
AUTO will be first item for ASOS/AWOS generated reports

2.    
ICAO Identifier (4-letter)

3.    
Issuance Time DDHHMMz (UTC)

·        
COR (CCD in Canada) if
correction to observation

4.    
Wind

·        
First 3 digits: True Wind direction or average if variable (VRB).

**Note:**
If the wind direction varies 60°
or more, the direction will be indicated with a V (e.g. 180V250)

·        
Next 2 digits: Mean speed and units

-       
KT=knots, KMH=kilometers/hour, MPS=meters/second

·        
G (gust) as needed – 2 or 3 digit maximum speed

·        
Calm will be indicated by 00000KT

·        
Example: 18012G22KT 150V240

5.    
Horizontal Visibility

·        
Prevailing Visibility (PV)

-       
Statue miles (SM) and fractions (US & Canada
only) **or**,

-       
4 digit minimum visibility in meters, **and**,

-       
Lowest value and direction, as required (shown as a remark)

 

·        
Runway
Visual Range
(RVR)

-       
R: Runway Designator, L/R/C as needed, “/”

-       
P/M: Plus/Minus (US only)

-       
4 digit value (feet/meters)

-       
V (variability) with tendency U/D/N (up/down/no change)

-       
Example: R18R/1200FTV/U

6.    
Present Weather (Constructed sequentially):

·        
Intensity

·        
Descriptor

·        
Precipitation (Dominant type is listed first if more than one type
reported)

·        
Obscuration

·        
Other

 

 

Qualifier

Weather Phenomena

Intensity or Proximity

Descriptor

Precipitation

Obscuration

Other

–

Light

BC

Patches

DZ

Drizzle

BR

Mist (1)

DS

Duststorm

BL

Blowing (2)

GR

Hail (3)

DU

Widespread Dust

No qualifier

Moderate

DR

Low Drifting (4)

GS

Small Hail and/or snow pellets (5)

FG

Fog (6)

FC

Funnel Clouds

FZ

Freezing

IC

Ice Crystals

FU

Smoke

PO

Dust/Sand Whirls

+

Heavy

MI

Shallow

PL

Ice Pellets

HZ

Haze

SQ

Squall(s)

PR

Partial

RA

Rain

SA

Sand

VC

Vicinity (7)

SH

Shower(s)

SG

Snow Grains

VA

Volcanic Ash

SS

Sandstorm

TS

Thunderstorm

SN

Snow

UP

Unknown Precipitation

(1)   
Visibility at least 1000m (5/8SM) but not more than 9600m
(6SM)

(2)   
6 feet or more above the ground

(3)   
Hailstone diameter 5mm or greater

(4)   
Less than 6 feet above the ground

(5)   
Hailstone diameter less than 5mm

(6)   
Visibility less than 1000m (5/8SM)

(7)   
Within 8KM (5SM) of the aerodrome but not at the aerodrome

 

7.    
Sky Cover

·        
Cloud Description

-       
Amount in eights (octas)

SKC=Sky Clear (clear below 12,000 for ASOS/AWOS)

NSC=No significant clouds

FEW=Few (1/8 to 2/8 sky cover)

SCT=Scattered (3/8 to 4/8 sky cover)

BKN=Broken (5/8 to 7/8 sky cover)

OVC=Overcast (8/8 sky cover)

8.    
Terperature/Dewpoint (whole °C) (preceded by M=minus)

·        
First 2 digits = temperature

·        
Second 2 digits = dewpoint

9.    
Altimeter setting (QNH) and indicator (A=InHg, Q=hPa)

10.
Supplementary Information

·        
RE = Recent weather followed by weather codes

·        
WS = Windshear, followed by:

-       
TKOF/LDG (takeoff/landing)

-       
RWY (2 digits runway identifier and designator L/R/C)

·        
RMK = Remark

-       
SLP = Sea Level Pressure

-       
T00221083 (Expanded temp/dewpoint)

1st, 5th digits: 0=plus, 1=minus

2nd-4th digits: temp (decimal missing)
(02.2)

6th-8th digits: dewpoint (decimal
missing) (-8.3)

11.
Trend Forecast (2 hours from time of observation) (Not used
in US)

·        
PROB and 2 digits (30 or 40) = probability 30% or 40%

·        
Used to indicate the probability of occurance of alternate element(s) or
temporary fluctuations

·        
Change Indicator

-       
BECMG = Becoming (used where changes are expected to reach or pass
through specified values

-       
TEMPO = Temporary (fluctuations of less than one hour duration

-       
NOSIG = No significant change

·        
Forecast Wind (same as item 4)

·        
Forecast Visibility (as item 5) (9999 indicates 10Kilometers vis or
greater)

·        
Forecast Weather (as item 6)

·        
Forecast Cloud (as item 7)

 

#### EIGHT FIGURE GROUP

An eight digit telegraphic code on runway conditions for
some European airports may be included at the end of hourly METAR
messages:

|  |  |
| --- | --- |
| Eight Figure Group | |
| 1st two digits | Runway designator |
| 3rd digit | Runway deposits |
| 4th digit | Extent of runway contamination |
| 5th and 6th digits | Depth of deposit |
| 7th and 8th digits | Friction coefficient or braking action |

 

The first two digits correspond to the runway designator. 
For parallel runways LEFT is indicated by the designator only (18L would
be displayed as 18) and RIGHT has 50 added (18R would be displayed as
68).  When all runways are affected the
figure group 88 will be used. 
If 99 appears as the first two digits the information is a
repetition of the last message because no new message has been received
in time for transmission.

 

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **Runway Deposits** | | **Extent of Runway Contamination** | | **Depth of Deposit** | |
| 0 | Clear & Dry | 1 | <10% contaminated (covered) | 00 | Less than 1mm |
| 1 | Damp | 2 | 11% to 25% contaminated (covered) | 01-90 | Measurement in mm |
| 2 | Wet or water particles | 92 | 10cm |
| 3 | Rime or frost covered (normally > 1mm) | 5 | 26%-50% contaminated (covered) | 93 | 15cm |
| 4 | Dry Snow | 9 | 51%-100% contaminated (covered) | 94 | 20cm |
| 5 | Wet Snow | 95 | 25cm |
| 6 | Slush | / | Not reported (runway clearance in progress) | 96 | 30cm |
| 7 | Ice | 97 | 35cm |
| 8 | Compacted or rolled snow |  |  | 98 | 40cm or more |
| 9 | Frozen ruts or ridges |  |  | 99 | Runway not operational due to snow, slush, ice, large drifts or runway clearance, depth not reported |
| / | Not reported (runway clearance in progress) |  |  | // | Not operationally significant or not measurable |

Note: the quoted depth is the mean of a number of reading or
if operationally significant the greatest depth measured.

|  |  |
| --- | --- |
| **Friction Coefficient or Braking Action (7th and 8th digits)** | |
| 28 | Friction coefficient 0.28 |
| 35 | Friction coefficient 0.35 |
| 91 | Braking action poor |
| 92 | Braking action medium to poor |
| 93 | Braking action medium |
| 94 | Braking action medium to good |
| 95 | Braking action good |
| 99 | Figures unreliable |
| // | Braking action not reported or runway not operations or airport closed. |

Note: Where braking action is assessed at a number of points
along the runway the mean value will be transmitted or if operationally
significant the lowest value.

If measuring equipment does not allow measurement of
friction with satisfactory reliability (such as contaminated by wet
snow, slush or loose snow) the figure 99 will be used.

 

### Automated Surface/Weather Observation System (ASOS/AWOS)

 

The Automated Surface Observation System (ASOS) and
Automated Weather Observation System (AWOS) observe and report altimeter
setting, wind direction and speed, temperature, dewpoint, visibility and
ceiling/cloud height. 
Pilots may use automated weather observation from ASOS/AWOS, provided
the observations from ASOS/AWOS, provided the observation includes all
necessary weather parameters, and that the system is installed, operated
and maintained according to applicable FAA standards.

Pilots may obtain the ASOS/AWOS reports through written,
radio or telephone methods. 
Refer to METAR section for ASOS/AWOS report format.

ASOS/AWOS observations may not be used as an authorized
weather observation if either the visibility or the wind is reported as
missing.

ASOS/AWOS observation are unusable for the purpose of
initiating or conducting an instrument approach if the altimeter setting
is reported as missing unless an approved alternate source is noted on
the applicable approach chart.

 

### TAF

Example:

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TAF | KRNO | 202320Z | 210024 | 04010G20KT | P6SM | -SN | SCT060 |
| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |

 

|  |  |  |  |
| --- | --- | --- | --- |
| FM0300 | 05008KT | P6SM | SCT060 |
| 9 |  |  |  |

```
 
```

1.    
Type of report (TAF)

2.    
ICAO Identifier (4
letter)

3.    
Issuance time (DDHHMM**Z**)
UTC.  May precede ICAO identifier at
some airports.

4.    
Day (DD).  Hour begins (1st two
digits XX) Hour ends (2nd two digits).

5.    
Wind. First 3 digits
true wind direction or average if variable.  If the wind varies 60° or more,
the direction will be indicated with a V (e.g. 120V190).  Next two digits Mean speed and
units (KT=knots, KMH=kilometers per hour, or MPS=meters per second).  G=gust as needed (2 or 3 digits). 
Calm will be indicated by 00000XXX (XXX will be replaced by the
appropriate units).

6.    
Horizontal
visibility.

a.     
Prevailing visibility (PV)

-       
Statute Miles
(SM) and fractions (US only), **or**

-       
4 digit minimum
visibility in meters, **and**

-       
Lowest value and
direction, as required

b.    
Runway Visual Range (RVR)

-       
R=Runway Designator,
L/R/C as needed, “/”

-       
P/M=Plus/Minus (US
Only)

-       
4 digit value
(feet/meters)

-       
V(variability) with
tendency U/D/N (up/down/no change)

7.    
Present Weather
(constructed sequentially):

·        
Intensity

·        
Descriptor

·        
Precipitation (Dominant type is listed first if more than one type
reported)

·        
Obscuration

·        
Other

 

 

Qualifier

Weather Phenomena

Intensity or Proximity

Descriptor

Precipitation

Obscuration

Other

–

Light

BC

Patches

DZ

Drizzle

BR

Mist (1)

DS

Duststorm

BL

Blowing (2)

GR

Hail (3)

DU

Widespread Dust

No qualifier

Moderate

DR

Low Drifting (4)

GS

Small Hail and/or snow pellets (5)

FG

Fog (6)

FC

Funnel Clouds

FZ

Freezing

IC

Ice Crystals

FU

Smoke

PO

Dust/Sand Whirls

+

Heavy

MI

Shallow

PL

Ice Pellets

HZ

Haze

SQ

Squall(s)

PR

Partial

RA

Rain

SA

Sand

VC

Vicinity (7)

SH

Shower(s)

SG

Snow Grains

VA

Volcanic Ash

SS

Sandstorm

TS

Thunderstorm

SN

Snow

UP

Unknown Precipitation

(8)   
Visibility at least 1000m (5/8SM) but not more than 9600m
(6SM)

(9)   
6 feet or more above the ground

(10)Hailstone
diameter 5mm or greater

(11)Less
than 6 feet above the ground

(12)Hailstone
diameter less than 5mm

(13)Visibility
less than 1000m (5/8SM)

(14)Within
8KM (5SM) of the aerodrome but not at the aerodrome

 

8.    
Sky Cover

·        
Cloud Description

-       
Amount in eights (octas)

SKC=Sky Clear (clear below 12,000 for ASOS/AWOS)

NSC=No significant clouds

FEW=Few (1/8 to 2/8 sky cover)

SCT=Scattered (3/8 to 4/8 sky cover)

BKN=Broken (5/8 to 7/8 sky cover)

OVC=Overcast (8/8 sky cover)

-       
Height: 100s of feet (30m)

-       
Type CB (Cumulonimbus) or TCU (Towering cumulus) only.

·        
CAVOK – Ceiling and visibility OK (not used in US).  Replaces visibility/RVR, present
weather, and clouds if:

-       
Visibility is 10KM or greater

-       
No CB and no cloud below 1500M (5000ft) or below highest minimum sector
altitude whichever is greater, and

-       
No precipitation, thunderstorm, sandstorm, duststorm, shallow fog, or
low drifting dust/sand/snow.

·        
Vertical visibility (when sky obscured) – VV100’s of feet (30m) (VV ///
means vertical visibility unavailable)

Optional groups (Forecast icing, Turbulence, & Temperature)

**T**=
Temperature group indicator

Temperature: two digits (if below 0°, will be preceded by
“M”),”/”

Expected time temperature will be reached: 2 digits, Z.

Icing Layer(s): 6 digits for each icing group (6WXXXY). 

6: first digit of the icing group is always a 6.

Icing type: Second digit:

|  |  |  |
| --- | --- | --- |
|  | **Icing Intensity** | **Location** |
| 0 | None | None |
| 1 | Light Icing |  |
| 2 | Light Icing | In cloud |
| 3 | Light Icing | In precipitation |
| 4 | Moderate |  |
| 5 | Moderate | In cloud |
| 6 | Moderate | In precipitation |
| 7 | Severe |  |
| 8 | Severe | In cloud |
| 9 | Severe | In precipitation |

Icing layer’s base: next 3 digits.  (direct reading in 100s of ft/30s
meters)

Thickness of icing layer: last digit:

|  |  |
| --- | --- |
|  | **Thickness of Layer** |
| 0 | Up to top of cloud |
| 1 | 300m/1000’ |
| 2 | 600m/2000’ |
| 3 | 900m/2000’ |
| 4 | 1200m/4000’ |
| 5 | 1500m/5000’ |
| 6 | 1800m/6000’ |
| 7 | 2100m/7000’ |
| 8 | 2400m/8000’ |
| 9 | 2700m/9000’ |

 

Turbulence Layer(s): 6 Digits (5WXXXY)

5: first digit of the turbulence group is always a 6.

Turbulence type: Second digit:

|  |  |  |  |
| --- | --- | --- | --- |
|  | **Intensity** | **Weather Condition** | **Frequency** |
| 0 | None |  |  |
| 1 | Light |  |  |
| 2 | Moderate | Clear | Occasional |
| 3 | Moderate | Clear | Frequent |
| 4 | Moderate | Cloud | Occasional |
| 5 | Moderate | Cloud | Frequent |
| 6 | Severe | Clear | Occasional |
| 7 | Severe | Clear | Frequent |
| 8 | Severe | Cloud | Occasional |
| 9 | Severe | Cloud | Frequent |

Turbulence layer’s base: next 3 digits.  (direct reading in 100s of ft/30s
meters)

Thickness of turbulence layer: last digit:

|  |  |
| --- | --- |
|  | **Thickness of Layer** |
| 0 | Up to top of cloud |
| 1 | 300m/1000’ |
| 2 | 600m/2000’ |
| 3 | 900m/2000’ |
| 4 | 1200m/4000’ |
| 5 | 1500m/5000’ |
| 6 | 1800m/6000’ |
| 7 | 2100m/7000’ |
| 8 | 2400m/8000’ |
| 9 | 2700m/9000’ |

 

 

SIGNIFICANT CHANGES IN FORECAST

1.    
Probability groups(s)

-       
PROB and 2 digits (30 or 40).

-       
Probability 30% or 40% used to
indicate the probability of occurrence of alternate element(s) or
temporary fluctuations.  (US
will only use 40%).  May
also be listed as TEMPO by some non US weather services.

-       
TIME (beginning 2 digits, ending 2
digits)

-       
Forecast weather phenomena.

2.    
Forecast Change

o      
Indicators

§        
BCMG=Becoming (used when changes
are expected to reach or pass through specified values)

§        
FM = From and 2 digit time

§        
TO = To and 2 digit time

§        
TEMPO = Temporary fluctuation

o      
Forecast weather phenomena.

 

### METAR /TAF Abbreviations / Cloud Types

 

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| A | Hail |  | AMOS | Automatic Meteorological observing system |
| ABM | Abeam |  |
| ABV | Above |  | AMS | Air mass |
| AC | Altocumulus |  | ANLYS | Analysis |
| ACCAS | Altocumulus castellanus |  | AO1 | Automated observation with no precip discriminator (rain/snow) |
| ACCUM | Altocumulate |  |
| ACLD | Above clouds |  | AO2 | Automated observation with precip discriminator (rain/snow) |
| ACSL | Standing lenticular altocumulus |  |
| ACTV | Active |  | AOA | At or above |
| ACYC | Anticyclonic |  | AOB | At or below |
| ADDN | Addition |  | AP | Anomalous propagation |
| ADRNDCK | Adirondack |  | APCH | Approach |
| ADVCTN | Advection |  | APRNT | Apparent |
| ADVY | Advisory |  | AS | Altostratus |
| AFDK | After Dark |  | ASOS | Automated surface observing system |
| AFT | After |  | ATLC | Atlantic |
| AFTN | Afternoon |  | ATTM | At this time |
| AGL | Above Ground Level |  | AURBO | Aurora Borealis |
| AGN | Again |  | AUTOB | Automatic weather reporting system |
| AHD | Ahead |  | AWOS | Automatic weather observing system |
| AIREP | Air Report |  | B | Beginning of precipitation (time in minutes (wx reports only) |
| AIRMET | Airmen’s Meteorological Info |  |
| ALF | Aloft |  | BACLIN | Baroclinic prognosis |
| ALG | Along |  | BATROP | Barotropic or barotropic prognosis |
| ALGHNY | Allegheny |  | BC | British Columbia |
| ALQDS | All quadrants |  | BCFG | Fog patches |
| ALSTG | Altimeter setting |  | BCKG | Backing |
| ALTA | Alberta |  | BCM(G) | Become (becoming) |
| ALUTN | Alleutian |  | BD | Blowing dust (wx reports only) |
| AMD | Amended forecast |  | BFDK | Before dark |
| AMDT | Amendment |  | BINOVC | Breaks in overcast |

 

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| BKN | Broken |  | CLD | Cloud |
| BLDUP | Build up |  | CLR | Clear |
| BLKHLS | Black Hills |  | CAS | Clear and smooth |
| BLO | Below |  | CNL | Cancel |
| BN | Blowing sand (wx reports only) |  | CNDN | Canadian |
| BNDRY | Boundary |  | CNTRL | Central |
| BOVC | Base of overcast |  | CNVG | Converge |
| BRAF | Braking action fair |  | CNVTV | Convective |
| BRAG | Braking action good |  | CONT-DVD | Continental Divide |
| BRAN | Braking action nil |  | CONTRAILS | Condensation trails |
| BRAP | Braking action poor |  | CS | Cirrostratus |
| BRF | Brief |  | CST | Coast |
| BRKSHR | Berkshire |  | CTGY | Category |
| BS | Blowing snow (wx reports only) |  | CTSKLS | Catskills |
| BTWN | Between |  | CU | Cumulus |
| BY | Blowing spray (wx reports only) |  | CUF | Cumuliform |
| CA | Clear above (PIREP only) |  | CUFRA | Cumulus fractus |
| CAN | Canada |  | CYC | Cyclonic |
| CARIB | Caribbean |  | CYCLGN | Cyclogenesis |
| CASCDS | Cascades |  | D | Dust (wx reports only) |
| CAVOK | Ceiling and visibility OK |  | DABRK | Daybreak |
| CAVU | Ceiling and visibility unlimited |  | DALGT | Daylight |
| CB | Cumulonimbus |  | DCAVU | Clear or scattered cloud and vis greater than 10, remainder or report missing (wx reports only) |
| CBMAM | Cumulonimbus mammatus |  |
| CC | Cirrocumulus |  |
| CCSL | Standing lenticular cirrocumulus |  | DCR | Decreased |
| CDFNT | Cold Front |  | DIAM | Diameter |
| CFP | Cold front passage |  | DKTS | Dakotas |
| CHC | Chance |  | DMSH | Diminish |
| CHSPK | Chesapeake |  | DNS | Dense |
| CIG | Ceiling |  | DNSLP | Downslope |

 

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| DNSTRM | Downstream |  | FLG | Falling |
| DP | Deep |  | FLRY | Flurry |
| DPNG | Deepening |  | FNT | Front |
| DPTH | Depth |  | FNTGNS | Frontogenesis |
| DRFT | Drift |  | FNTLYS | Frontolysis |
| DRZL | Drizzle |  | FORNN | Forenoon |
| DSIPT | Dissipate |  | FRMG | Forming |
| DSNT | Distant |  | FROPA | Frontal passage |
| DTRT | Deteriorate |  | FRST | Frost |
| DRG | During |  | FRZ | Freeze |
| DWNDFTS | Downdrafts |  | FRZLVL | Freezing level |
| DWPNT | Dew point |  | FRZN | Frozen |
| E | Ending of precipitation (time in minutes)(wx reports only) |  | FZRANO | Freezing rain sensor not operating |
|  | FT | Terminal Forecast |
| E | Equatorial (air mass) |  | G | Gusts reaching (knots)(wx reports only) |
| E | Estimated (wx reports only) |  | GF | Ground fog (wx reports only) |
| ELNGT | Elongate |  | GFDEP | Ground fog estimated (feet) deep |
| EMBDD | Embedded |  | GICG | Glaze icing |
| ENRT | Enroute |  | GLFALSK | Gulf of Alaska |
| ENTR | Entire |  | GLFCAL | Gulf of California |
| ERY | Early |  | CLFMEX | Gulf of Mexico |
| EVE | Evening |  | GLFSTLAWR | Gulf of St. Lawrence |
| EXCP | Except |  | GNDFG | Ground Fog |
| EXPC | Expect |  | GRAD | Gradient |
| EXTRM | Extreme |  | GRTLKS | Great Lakes |
| F | Fog (wx reports only) |  | GSTS | Gusts |
| FA | Area Forecast |  | GSTY | Gusty |
| FAH | Farenheit |  | H | Haze (wx reports only) |
| FAX | Facsimile |  | HCVIS | High clouds visible |
| FIBI | Filed but impracticable to transmit |  | HDEP | Haze layer estimated (feet) deep |
| FINO | Wx report will not be filed for transmission |  | HDSVLY | Hudson Valley |

 

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| HI | High |  | LABRDR | Labrador |
| HLSTO | Hailstones |  | LFT | Lift |
| HLYR | Haze layer aloft |  | LGT | Light |
| HURCN | Hurricane |  | LIFR | Low IFR (wx reports only) |
| HVY | Heavy |  | LK | Lake |
| IC | Ice crystal |  | LSR | Loose snow on runway |
| ICG | Icing |  | LST | Local Standard Time |
| ICGIC | Icing in clouds |  | LTGCA | Lightning cloud to air |
| ICGICIP | Icing in clouds and precipitation |  | LTGCC | Lightning cloud to cloud |
| ICGIP | Icing in precipitation |  | LTGCCCG | Lightning cloud to cloud, cloud to ground |
| IF | Ice fog |  | LTGCG | Lightning cloud to ground |
| IFR | Instrument flight rules |  | LTGCW | Lightning cloud to water |
| INCR | Increase |  | LTGIC | Lightning in clouds |
| INDC | Indicate |  | LTLCG | Little change |
| INDEF | Indefinite |  | LTNG | Lightning |
| INLD | Inland |  | LYR | Layer or layered or layers |
| INSTBY | Instability |  | M | Measured ceiling (wx reports only) |
| INTR | Interior |  | M | Missing (wx reports only) |
| INTR-MTRGN | Inter-mountain region |  | MAN | Manitoba |
| INTS | Intense |  | MDT | Moderate |
| INTST | Intensity |  | METAR | Scheduled aviation observation |
| INVRN | Inversion |  | MEX | Mexico |
| IOVC | In overcast |  | MHKVLY | Mohawk Valley |
| IP | Ice pellets (wx reports only) |  | MIDN | Midnight |
| IR | Ice on runway |  | MIFG | Patches of shallow fog not deeper than 2 meters |
| JTSTR | Jetstream |  | MLTLVL | Melting level |
| K | Smoke |  | MNLD | Mainland |
| KDEP | Smoke layer estimated (feet) deep |  | MOGR | Moderate or greater |
| KLYR | Smoke layer aloft |  | MOV | Move |
| KOCTY | Smoke over city |  | MRGL | Marginal |
| L | Drizzle (wx reports only) |  | MRNG | Morning |

 

 

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| MRTM | Maritime |  | PGTSND | Puget Sound |
| MSTLY | Mostly |  | PIBAL | Pilot balloon observation |
| MTN | Mountain |  | PK WND | Peak wind (wx report only) |
| MVFR | Marginal VFR |  | PNHDL | Panhandle |
| NB | New Brunswick |  | PNO | Rain gauge not operating |
| NEW ENG | New England |  | PPINA | Radar weather report not available or omitted |
| NFLD | Newfoundland |  |
| NGT | Night |  | PPINE | Radar weather report no echoes observed |
| NOSPL | No special observations taken (wx reports only) |  | PPINO | Radar weather report equipment inoperative due to breakdown |
| NS | Nimbostratus |  | PPIOK | Radar weather report equipment operation resumed |
| NS | Nova Scotia |  |
| NVA | Negative vorticity advection |  | PPIOM | Radar weather report equipment inoperative due to maintenance |
| OBS | Observation |  |
| OBSC | Obscure |  | PRBLTY | Probability |
| OCFNT | Occluded front |  | PRESFR | Pressure falling rapidly |
| OCLD | Occlude |  | PRESRR | Pressure rising rapidly |
| OCLN | Occlusion |  | PRJMP | Pressure jump (wx reports only) |
| OFP | Occluded frontal passage |  | PROG | Prognosis or prognostic |
| OFSHR | Offshore |  | PSR | Packed snow on runway |
| OMTNS | Over mountains |  | PTCHY | Patchy |
| ONSHR | On shore |  | PTLY | Partly |
| ONT | Ontario |  | PVA | Positive vorticity advection |
| ORGPHC | Orographic |  | PWINO | Precipitaion identifier information not available (wx reports only) |
| OTAS | On top and smooth |  | Q | Squall (wx reports only) |
| OTLK | Outlook |  | QSTNRY | Quasistationary |
| OVC | Overcast |  | QUE | Quebec |
| OVR | Over |  | R | Rain (wx reports only) |
| PAC | Pacific |  | RADAT | Radiosonde observation data |
| PCPN | Precipitation |  | RAOB | Radiosonde observation |
| PDW | Priority Delayed Weather |  | RCKY | Rocky Mountains |
| PEN | Peninsula |  | RDG | Ridge |

 

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| RGD | Ragged |  | TDWR | Terminal Doppler Weather Radar |
| RHINO | Radar echo height information not available |  | TEMP | Temperature |
| RHINO | Radar range height indicator not operating on scan |  | THDR | Thunder |
| RIOGD | Rio Grande |  | THRU | Through |
| RNFL | Rainfall |  | THRUT | Throughout |
| ROBEPS | Radar operating below prescribed standard |  | THSD | Thousand |
| RPD | Rapid |  | TIL | Until |
| RSG | Rising |  | TMW | Tomorrow |
| RUF | Rough |  | TNGT | Tonight |
| RVRNO | Runway visual range missing |  | TOP | Cloud top |
| RW | Rain shower (wx reports only) |  | TOVC | Top of overcast |
| S | Snow (wx reports only) |  | TPG | Topping |
| SASK | Saskatchewan |  | TROF | Trough |
| SAWRN | Supplementary Aviation Weather Reporting System |  | TROP | Tropopause |
| SC | Stratocumulus |  | TRPCL | Tropical |
| SCSL | Stratocumulus standing lenticular |  | TRRN | Terrain |
| SCT | Scattered |  | TSHWR | Thundershower |
| SELS | Severe local storms |  | TSNO | Lightning sensor not available |
| SFERICS | Atmospherics |  | TSTM | Thunderstorm |
| SG | Snow grains (wx reports only) |  | TURB | Turbulence |
| SHFT | Shift (wx reports only) |  | TURBC | Turbulence |
| SHLW | Shallow |  | TWD | Toward |
| SHWR | Shower |  | TWR | Tower |
| SIERNEV | Sierra Nevada |  | TWRG | Towering |
| SIR | Snow and ice on runway |  | TYPH | Typhoon |
| SPECI | Unscheduled aviation observation |  | U | Intensity unknown (wx reports only) |
| SLF | Sea level pressure |  | UA | Routine PIREP |
| SLPNO | Sea level pressure not available |  | UDDF | Up and down drafts |
| SNINCR | Snow increasing rapidly |  | UNSTBL | Unstable |
| TCU | Towering cumulus |  | UNSTDY | Unsteady |
| TDA | Today |  | UPR | Upper |

 

 

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| UTC | Universal coordinated time |  | WND | Wind |
| UUA | Urgent PIREP |  | WRM | Warm |
| V | Variable (wx reports only) |  | WRMFNT | Warm front |
| VCSH | Showers in vicinity |  | WRNG | Warning |
| VCTY | Vicinity |  | WSHFT | Wind shift |
| VFR | Visual flight rules |  | WW | Severe weather forecast |
| VLY | Valley |  | WX | Weather |
| VRBL | Variable |  | X | Obscured sky condition |
| VSBY | Visibility |  | XCP | Except |
| WDLY | Widely |  | YDA | Yesterday |
| WEA | Weather |  | Z | UTC |
| WFP | Warm front passage |  | ZRNO | Freezing rain information not available (wx reports only) |
| WK | Weak |  |
| WKN | Weaken |  |  |  |
| WL | Will |  |  |  |

 

 

### AIRMETs

 

Hazardous weather advisories of **moderate** intensity will be issued
as AIRMETs.  AIRMETs are
issued when the following conditions are expected to cover an area of at
least 3000 square miles:

Moderate icing.

Moderate turbulence.

Sustained surface winds of 30 knots or more.

Ceilings less than 1,000 ft. and/or visibility less than 3
miles affecting 50% of an area at one time.

Extensive mountain obscuration.

 

### SIGMET's

 

Hazardous weather advisories of **severe** intensity will be issued
as SIGMETs.  SIGMETs are
reported as convective or nonconvective.

Convective SIGMETs report only thunderstorms and related
phenomena (tornadoes, heavy precipitation, hail and high surface winds.

Nonconvective SIGMETs are issued when the following
conditions occur or are expected to cover an area of at least 3,000
square miles:

Severe or extreme turbulence or clear air
turbulence (CAT) not associated with thunderstorms.

Severe icing not associated with thunderstorms.

Widespread duststorms, sandstorms, or volcanic
ash lowering surface or inflight visibilities to below three miles.

Volcanic eruption.

 

Volcanic eruption SIGMET's are identified by an alphanumeric
designator which consists of an alphabetic identifier and issuance
number. The first time an advisory is issued for a phenomenon associated
with a particular weather system, it will be given the next alphabetic
designator in the series and will be numbered as the first for that
designator. Subsequent advisories will retain the same alphabetic
designator until the phenomenon ends. In the conterminous U.S., this means that a
phenomenon that is assigned an alphabetic designator in one area will
retain that designator as it moves within the area or into one or more
other areas. Issuance’s for the same phenomenon will be sequentially
numbered, using the same alphabetic designator until the phenomenon no
longer exists. Alphabetic designators NOVEMBER through YANKEE, except
SIERRA and TANGO are only used for SIGMET's, while designators SIERRA,
TANGO and ZULU are used for AIRMET's.

 

### Pilot Weather Report (PIREP)

 

Pilots
must report any significant weather or flight condition to ATC as soon
as possible. Additionally, all significant weather or flight conditions
that clearly differ from the forecast should be reported to Dispatch.  There is no specific format for
this type of report.

**NOTE:** Report windshear encountered
during departure or approach to the tower controller as soon as
possible.Use the term
PIREP to ensure that it is rebroadcast.

﻿
