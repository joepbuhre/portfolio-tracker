<template>
    <!-- <TheTimeLine>
        
    </TheTimeLine>     -->
    <IuTable :rows="getRows" :headers="getHeaders">
        <Column v-for="(display, key) of getHeaders" :display-name="display.name" :column-name="key" sorting-enabled />
    </IuTable>
</template>

<script setup lang="ts">

import { Column, IuTable } from "@IuComponentLib/TheTable";
import TheTimeLine from "@components/TheTimeLine.vue";
import { computed } from "vue";

const getHeaders = {
    description: { name: "Description" },
    ticker: { name: "Ticker" },
    totalValue: { name: "Portfolio gewicht" },
    quantity: { name: "Quantity" },
    percentage: { name: "Percentage" },
};

const getRows = computed(() => [
    {
        description: "ABN AMRO GROUP",
        ticker: "ABN.AS",
        totalValue: 123.7,
        quantity: 10.0,
        percentage: 0.0386,
    },
    {
        description: "ADVANCED MICRO DEVICES",
        ticker: "AMD",
        totalValue: 668.6926,
        quantity: 6.0,
        percentage: 0.2086,
    },
    {
        description: "AMAZON.COM INC. - COM",
        ticker: "AMZN",
        totalValue: 539.9559,
        quantity: 4.0,
        percentage: 0.1684,
    },
    {
        description: "APPLE INC. - COMMON ST",
        ticker: "AAPL",
        totalValue: 526.7352,
        quantity: 3.0,
        percentage: 0.1643,
    },
    {
        description: "ING GROEP N.V.",
        ticker: "INGA.AS",
        totalValue: 141.702,
        quantity: 11.0,
        percentage: 0.0442,
    },
    {
        description: "PRYSMIAN",
        ticker: "PRY.MI",
        totalValue: 182.5,
        quantity: 5.0,
        percentage: 0.0569,
    },
    {
        description: "VANECK MORNINGSTAR DEVELOPED MARKETS DIVIDEND LEADER...",
        ticker: "TDIV.AS",
        totalValue: 388.575,
        quantity: 11.0,
        percentage: 0.1212,
    },
    {
        description: "VANGUARD S&P500",
        ticker: "VUSA.AS",
        totalValue: 633.704,
        quantity: 8.0,
        percentage: 0.1977,
    },
]);
</script>
