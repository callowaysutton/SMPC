/*
Template Name: HUD - Responsive Bootstrap 5 Admin Template
Version: 3.0.0
Author: Sean Ngu
Website: http://www.seantheme.com/hud/
*/

var randomNo = function() {
  return Math.floor(Math.random() * 60) + 30
};

var handleRenderChart = function() {
	// global apexchart settings
	Apex = {
		title: {
			style: {
				fontSize:  '14px',
				fontWeight:  'bold',
				fontFamily:  app.font.bodyFontfamily,
				color:  app.color.bodyColor
			},
		},
		legend: {
			fontFamily: app.font.bodyFontfamily,
			labels: {
				colors: app.color.bodyColor
			}
		},
		tooltip: {
			style: {
        fontSize: '12px',
        fontFamily: app.font.bodyFontfamily
      }
		},
		grid: {
			borderColor: 'rgba('+ app.color.bodyColorRgb + ', .25)',
		},
		dataLabels: {
			style: {
				fontSize: '12px',
				fontFamily: app.font.bodyFontfamily,
				fontWeight: 'bold',
				colors: undefined
  		}
		},
		xaxis: {
			axisBorder: {
				show: true,
				color: 'rgba('+ app.color.bodyColorRgb + ', .25)',
				height: 1,
				width: '100%',
				offsetX: 0,
				offsetY: -1
			},
			axisTicks: {
				show: true,
				borderType: 'solid',
				color: 'rgba('+ app.color.bodyColorRgb + ', .25)',
				height: 6,
				offsetX: 0,
				offsetY: 0
			},
      labels: {
				style: {
					colors: app.color.bodyColor,
					fontSize: '12px',
					fontFamily: app.font.bodyFontfamily,
					fontWeight: 400,
					cssClass: 'apexcharts-xaxis-label',
				}
			}
		},
		yaxis: {
      labels: {
				style: {
					colors: app.color.bodyColor,
					fontSize: '12px',
					fontFamily: app.font.bodyFontfamily,
					fontWeight: 400,
					cssClass: 'apexcharts-xaxis-label',
				}
			}
		}
	};
  
  
  // small stat chart
	var x = 0;
	var chart = [];
	
	var elmList = [].slice.call(document.querySelectorAll('[data-render="apexchart"]'));
	elmList.map(function(elm) {
		var chartType = elm.getAttribute('data-type');
		var chartHeight = elm.getAttribute('data-height');
		var chartTitle = elm.getAttribute('data-title');
		var chartColors = [];
		var chartPlotOptions = {};
		var chartData = [];
		var chartStroke = {
			show: false
		};
		if (chartType == 'bar') {
			chartColors = [app.color.theme];
			chartPlotOptions = {
				bar: {
					horizontal: false,
					columnWidth: '65%',
					endingShape: 'rounded'
				}
			};
			chartData = [{
				name: chartTitle,
				data: [randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo()]
			}];
		} else if (chartType == 'pie') {
			chartColors = ['rgba('+ app.color.themeRgb + ', 1)', 'rgba('+ app.color.themeRgb + ', .75)', 'rgba('+ app.color.themeRgb + ', .5)'];
			chartData = [randomNo(), randomNo(), randomNo()];
		} else if (chartType == 'donut') {
			chartColors = ['rgba('+ app.color.themeRgb + ', .15)', 'rgba('+ app.color.themeRgb + ', .35)', 'rgba('+ app.color.themeRgb + ', .55)', 'rgba('+ app.color.themeRgb + ', .75)', 'rgba('+ app.color.themeRgb + ', .95)'];
			chartData = [randomNo(), randomNo(), randomNo(), randomNo(), randomNo()];
			chartStroke = {
				show: false,
				curve: 'smooth',
				lineCap: 'butt',
				colors: 'rgba(' + app.color.bodyColorRgb + ', .25)',
				width: 2,
				dashArray: 0,    
			};
			chartPlotOptions = {
				pie: {
					donut: {
						background: 'transparent',
					}
				}
			};
		} else if (chartType == 'line') {
			chartColors = [app.color.theme];
			chartData = [{
				name: chartTitle,
				data: [randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo()]
			}];
			chartStroke = {
				curve: 'straight',
				width: 2
			};
		}
	
		var chartOptions = {
			chart: {
				height: chartHeight,
				type: chartType,
				toolbar: {
					show: false
				},
				sparkline: {
					enabled: true
				},
			},
			dataLabels: {
				enabled: false
			},
			colors: chartColors,
			stroke: chartStroke,
			plotOptions: chartPlotOptions,
			series: chartData,
			grid: {
				show: false
			},
			tooltip: {
				theme: 'dark',
				x: {
					show: false
				},
				y: {
					title: {
						formatter: function (seriesName) {
							return ''
						}
					},
					formatter: (value) => { return ''+ value },
				}
			},
			xaxis: {
				labels: {
					show: false
				}
			},
			yaxis: {
				labels: {
					show: false
				}
			}
		};
		chart[x] = new ApexCharts(elm, chartOptions);
		chart[x].render();
		x++;
	});
  
  var serverChartOptions = {
    chart: {
      height: '100%',
      type: 'bar',
      toolbar: {
        show: false
      }
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '55%',
        endingShape: 'rounded'  
      },
    },
    dataLabels: {
      enabled: false
    },
    grid: {
    	show: true,
    	borderColor: 'rgba('+ app.color.bodyColorRgb +', .15)',
    },
    stroke: {
      show: false
    },
    colors: ['rgba('+ app.color.bodyColorRgb + ', .25)', app.color.theme],
    series: [{
    	name: 'MEMORY USAGE',
      data: [
      	randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(),
      	randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo()
      ]
    },{
    	name: 'CPU USAGE',
      data: [
      	randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(),
      	randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo(), randomNo()
      ]
    }],
    xaxis: {
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      labels: {
				show: false
			}
    },
    fill: {
      opacity: .65
    },
    tooltip: {
      y: {
        formatter: function (val) {
          return "$ " + val + " thousands"
        }
      }
    }
  };
  var apexServerChart = new ApexCharts(
    document.querySelector('#chart-server'),
    serverChartOptions
  );
  apexServerChart.render();
};

/* Controller
------------------------------------------------ */
$(document).ready(function() {
	handleRenderChart();
	
	document.addEventListener('theme-reload', function() {
		$('[data-render="apexchart"], #chart-server').empty();
		handleRenderChart();
	});
});