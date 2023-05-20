<template>
    <div id="chart"></div>
</template>

<script setup lang="ts">
import ApexCharts from 'apexcharts'
import { onMounted } from 'vue'


export interface TickerHistory {
    id: string
    share_id: string
    price: number
    date: string
    ticker: string,
    growth: number
}

const props = defineProps<{
    history: {[key: string]: TickerHistory[]}
}>()

onMounted(() => {
    const ticker = Object.entries(props.history)[0][1]
    var options = {
        series: Object.entries(props.history).map(tickers => ({
            name: tickers[0],
            data: tickers[1].map(el => ({x: el.date, y: el.growth}))
        })),
          chart: {
          type: 'area',
          stacked: false,
          height: 350,
          zoom: {
            type: 'x',
            enabled: true,
            autoScaleYaxis: true
          },
          toolbar: {
            autoSelected: 'zoom'
          }
        },
        dataLabels: {
          enabled: false
        },
        markers: {
          size: 0,
        },
        title: {
          text: 'Stock Price Movement',
          align: 'left'
        },
        fill: {
          type: 'gradient',
          gradient: {
            shadeIntensity: 1,
            inverseColors: false,
            opacityFrom: 0.5,
            opacityTo: 0,
            stops: [0, 90, 100]
          },
        },
        yaxis: {
          labels: {
            formatter: function (val: any) {
              return (val * 100).toFixed(2) + "%";
            },
          },
          title: {
            text: 'Price'
          },
        },
        xaxis: {
          type: 'datetime',
        },
        tooltip: {
          shared: true,
          y: {
            formatter: function (val: any) {
                return (val * 100).toFixed(2) + "%";
            }
          }
        }
        };
        //@ts-ignore
        window.chart = new ApexCharts(document.querySelector("#chart"), options);
        //@ts-ignore
        window.chart.render();

})



</script>