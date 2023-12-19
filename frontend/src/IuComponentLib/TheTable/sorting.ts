import { ref } from "vue";
import { direction } from "./enums";
import { Row } from "./types";

export const dir = ref<direction>(direction.ASC);

export const srtVal = ref<keyof Row | null>(null);

export const doSorting = (key: keyof Row) => {
    if (srtVal.value === key) {
        if (dir.value === direction.ASC) {
            dir.value = direction.DESC;
        } else {
            dir.value = direction.ASC;
        }
    } else {
        srtVal.value = key;
        dir.value = direction.ASC;
    }
};

export const sortFunction = (a: any, b: any) => {
    if (srtVal.value === null) return 0;

    let resp;
    if (a[srtVal.value] < b[srtVal.value]) {
        resp = -1;
    } else if (a[srtVal.value] > b[srtVal.value]) {
        resp = 1;
    } else {
        resp = 0;
    }

    return resp * dir.value;
};
