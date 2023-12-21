import { ref } from "vue"

export const filterValues = ref<{[key: string]: any[]}>({})

export const doFiltering = (key: string, vals: any[]) => {
    filterValues.value[key] = vals
}

export const filterFunction = (e: any) => {
    return Object.entries(filterValues.value).every(([key, values]) => {
        if(values.length === 0) return true
        return values.includes(e[key])
    });
}

    
//     return true
// }

// export const tst = (e) => {
//     return Object.entries(filterValues.value).every(([key, values]) => values.includes(obj[key]));
// }