<template>
    <div id="chart"></div>
</template>

<script setup lang="ts">
import { EuroFormatter } from "@src/utils/formatters";
import ApexCharts from "apexcharts";
import { onMounted } from "vue";

export interface TickerTotalValue {
    date: string;
    total_value: number;
}

const props = defineProps<{
    history: TickerTotalValue[];
}>();

const generateColors = (dt: typeof props.history) => {
    let returning = dt.map((d: TickerTotalValue, idx: number) => {
        let color = d.total_value > 2000 ? "#00c263" : "#fa4646";
        return {
            offset: (idx / dt.length) * 100,
            color: color,
            opacity: 1,
        };
    });
    return returning;
};
onMounted(() => {
    var options: ApexCharts.ApexOptions = {
        series: [
            {
                name: "Total",
                data: props.history.map((el) => ({
                    x: el.date,
                    y: el.total_value,
                })),
            },
        ],
        chart: {
            type: "line",
            height: 350,
            zoom: {
                type: "x",
                enabled: true,
                autoScaleYaxis: true,
            },
            toolbar: {
                autoSelected: "zoom",
            },
        },
        dataLabels: {
            enabled: false,
        },
        markers: {
            size: 0,
        },

        title: {
            text: "Stock Price Movement",
            align: "left",
        },
        fill: {
            type: "gradient",
            gradient: {
                type: "vertical",
                shadeIntensity: 1,
                opacityFrom: 1,
                opacityTo: 1,
                colorStops: generateColors(props.history),
            },
        },
        yaxis: {
            labels: {
                formatter: EuroFormatter.format,
            },
            title: {
                text: "Price",
            },
        },
        xaxis: {
            type: "datetime",
        },
        tooltip: {
            shared: true,
            y: {
                formatter: EuroFormatter.format,
            },
        },
    };
    //@ts-ignore
    window.chart = new ApexCharts(document.querySelector("#chart"), options);
    //@ts-ignore
    window.chart.render();
});
</script>
