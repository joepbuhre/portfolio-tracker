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
            <table
                class="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400"
            >
                <thead
                    class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400"
                >
                    <tr>
                        <th
                            scope="col"
                            class="px-6 py-3 text-left"
                            v-for="desc in [
                                'Description',
                                'Ticker',
                                'Portfolio gewicht',
                                'Quantity',
                                'Percentage',
                            ]"
                        >
                            {{ desc }}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr
                        v-for="stock in stocks"
                        class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 text-left"
                    >
                        <th class="px-6 py-2">{{ stock.description }}</th>
                        <td class="px-6 py-2">{{ stock.ticker }}</td>
                        <td class="px-6 py-2">
                            {{ EuroFormatter.format(stock.totalValue) }}
                        </td>
                        <td class="px-6 py-2">{{ stock.quantity }}</td>
                        <td class="px-6 py-2">
                            {{ PercentageFormatter.format(stock.percentage) }}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import PrestationCard, {
    PrestationCardProps,
} from "../components/PrestationCard.vue";
import { useMain } from "../store/main";
import { api } from "../utils/api";
import { EuroFormatter, PercentageFormatter } from "../utils/formatters";
import type { TickerHistory } from "../components/GraphLine.vue";
import GraphLine from "../components/GraphLine.vue";

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
