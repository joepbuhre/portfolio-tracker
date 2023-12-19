<template>
    <h1 class="font-light text-3xl py-4">Prestaties</h1>
    <div class="flex gap-5">
        <PrestationCard v-for="card in cards" class="w-1/4" v-bind="card" />
    </div>
    <div class="my-8">
        <GraphLine :history="history" v-if="Object.keys(history).length > 0" />
    </div>
    <div></div>
    <div>
        <div class="relative overflow-x-auto">
            <IuTable
                :rows="stocks"
                :headers="{
                    description: {
                        name: 'Description',
                    },
                    ticker: {
                        name: 'Ticker',
                    },
                    totalValue: {
                        name: 'Portfolio gewicht',
                        formatter: EuroFormatter,
                    },
                    quantity: {
                        name: 'Quantity',
                    },
                    percentage: {
                        name: 'Percentage',
                        formatter: PercentageFormatter,
                    },
                }"
            />
        </div>
    </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import PrestationCard, {
    PrestationCardProps,
} from "@components/PrestationCard.vue";
import { useMain } from "../store/main";
import { api } from "../utils/api";
import { EuroFormatter, PercentageFormatter } from "../utils/formatters";
import type { TickerHistory } from "@components/GraphLine.vue";
import GraphLine from "@components/GraphLine.vue";
import { IuTable } from "@IuComponentLib/TheTable";

onMounted(() => {
    fetchHistory();
    fetchStocks();
});

// Store setup
const main = useMain();

const history = ref<{ [key: string]: TickerHistory[] }>({});
const fetchHistory = () => {
    api.get("/stocks/history").then((res) => {
        const data = res.data;
        history.value = <{ [key: string]: TickerHistory[] }>data;
    });
};

const fetchStats = () => {
    api.get('/stocks/stats').then(res => {
        
    })
}

interface stocks {
    description: string;
    ticker: string;
    totalValue: number;
    quantity: number;
    percentage: number;
}

const stocks = ref<stocks[]>([]);
const fetchStocks = () => {
    api.get("/stocks").then((res) => {
        stocks.value = res.data;
    });
};

const cards = computed((): PrestationCardProps[] => [
    {
        title: "Total Value",
        currentValue: stocks.value.reduce((accumulator, currentValue) => {
            return accumulator + currentValue.totalValue;
        }, 0),
        currentValueFormat: EuroFormatter,
        differenceValue: -11.8 / 100,
        differenceValueFormat: PercentageFormatter,
    },
    {
        title: "Profit",
        currentValue: 0,
        currentValueFormat: EuroFormatter,
        differenceValue: 0
    },
    {
        title: "Dividend",
        currentValue: 40,
        currentValueFormat: EuroFormatter,
        differenceValue: 10 / 100,
        differenceValueFormat: PercentageFormatter,
    },
    {
        title: "Total Cost",
        currentValue: 10.9,
        currentValueFormat: EuroFormatter,
        differenceValue: -11.8 / 100,
        differenceValueFormat: PercentageFormatter,
    },
]);
</script>
