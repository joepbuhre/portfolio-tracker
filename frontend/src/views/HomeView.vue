<template>
    <h1 class="py-4 text-3xl font-light">Prestaties</h1>
    <div class="flex gap-5">
        <PrestationCard v-for="card in cards" class="w-1/4" v-bind="card" />
    </div>
    <div class="my-8">
        <GraphTotalValue
            :history="history_value"
            v-if="history_value && Object.keys(history_value).length > 0"
        />
    </div>
    <div></div>
    <div>
        <div class="relative overflow-x-auto">
            <IuTable
                :rows="stocks"
                :error-msg="errorMsg"
                :axios-instance="api"
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
import type { TickerTotalValue } from "@components/GraphTotalValue.vue";
import GraphTotalValue from "@components/GraphTotalValue.vue";
import { IuTable } from "@IuComponentLib/TheTable";
import { AxiosError } from "axios";

onMounted(() => {
    fetchHistoryValue();
    fetchStocks();
    fetchStats();
});

// Store setup
const main = useMain();

const errorMsg = ref<string | undefined>(undefined);

// const fetchHistory = () => {
//     api.get("/stocks/history")
//         .then((res) => {
//             const data = res.data;
//             history.value = <{ [key: string]: TickerHistory[] }>data;
//             console.log("oeps");
//         })
//         .catch((err: AxiosError) => {});
// };

const stats = ref<null | DashboardStats>(null);
const fetchStats = () => {
    api.get("/stocks/dashboard-stats").then((res) => {
        stats.value = res.data;
    });
};

interface stocks {
    description: string;
    ticker: string;
    totalValue: number;
    quantity: number;
    percentage: number;
}

interface DashboardStats {
    total_value: number;
    xirr: number;
    dividend: number;
    total_cost: number;
    value_change: number;
}

const history_value = ref<TickerTotalValue[]>([]);
const fetchHistoryValue = () => {
    api.get("/stocks/total-value").then((res) => {
        history_value.value = res.data;
    });
};

const stocks = ref<stocks[]>([]);
const fetchStocks = () => {
    api.get("/stocks").then((res) => {
        stocks.value = res.data;
    });
};

const currentValue = computed(() => {
    return stocks.value.reduce((accumulator, currentValue) => {
        return accumulator + currentValue.totalValue;
    }, 0);
});

const cards = computed((): PrestationCardProps[] => [
    {
        title: "Total Value",
        currentValue: currentValue.value,
        currentValueFormat: EuroFormatter,
        differenceValue: stats.value?.xirr ?? 0,
        differenceValueFormat: PercentageFormatter,
    },
    {
        title: "Value change",
        currentValue: stats.value?.value_change ?? 0,
        currentValueFormat: EuroFormatter,
        differenceValue:
            currentValue.value /
                (currentValue.value - (stats.value?.value_change ?? 0)) -
            1,
        differenceValueFormat: PercentageFormatter,
    },
    {
        title: "Yield",
        currentValue: stats.value?.xirr ?? 0,
        currentValueFormat: PercentageFormatter,
    },
    {
        title: "Dividend",
        currentValue: stats.value?.dividend ?? 0,
        currentValueFormat: EuroFormatter,
        differenceValue: 10 / 100,
        differenceValueFormat: PercentageFormatter,
    },
    {
        title: "Total Cost",
        currentValue: -(stats.value?.total_cost ?? 0),
        currentValueFormat: EuroFormatter,
        differenceValue: -11.8 / 100,
        differenceValueFormat: PercentageFormatter,
    },
]);
</script>
