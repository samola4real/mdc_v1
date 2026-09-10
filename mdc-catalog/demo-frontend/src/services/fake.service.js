import axios from "axios";

export const FakeService = {
    getInstances,
    getInstancesAxios,
    getFakeInstances
}

// TODO: replace API_URL with your real endpoint before calling these helpers.
const API_URL = '';

// This is a fake service that returns a promise with a list of products using fetch API.
function getInstances() {
    if (!API_URL) {
        return Promise.reject(new Error('FakeService.getInstances: API_URL is not configured'));
    }
    return fetch(API_URL, { headers: { 'Cache-Control': 'no-cache' } })
        .then((res) => res.json())
        .then((d) => d.data);
}

// This is a fake service that returns a promise with a list of products using axios API.
function getInstancesAxios() {
    if (!API_URL) {
        return Promise.reject(new Error('FakeService.getInstancesAxios: API_URL is not configured'));
    }
    return axios
        .get(API_URL, { headers: { 'Content-Type': 'application/json' } })
        .then((res) => res.data.data)
        .catch((error) => {
            console.error(error);
            throw error;
        });
}

function getFakeInstances() {
    // let allInstances = instances.filter(item => item.id !== 'new');
    return Promise.resolve(instances);
}

const instances= [
    { "id":"1", "name": "Joan F.", "startDate": "23-10-2020", "endDate": "13-02-2021", "status": "qualified", "description":""},
    { "id":"2", "name": "Mark L.", "startDate": "23-4-2020", "endDate": "15-10-2021", "status": "new", "description":"" },
    { "id":"3", "name": "Lucy G.", "startDate": "15-6-2020", "endDate": "13-11-2021", "status": "qualified", "description":"" },
    { "id":"4", "name": "Emmanuel X.", "startDate": "23-12-2020", "endDate": "21-05-2021", "status": "unqualified", "description":"" },
    { "id":"5", "name": "Jean G.", "startDate": "2-10-2020", "endDate": "03-03-2021", "status": "new", "description":"" },
    { "id":"6", "name": "Asiya M.", "startDate": "19-7-2020", "endDate": "18-02-2021", "status": "new", "description":"" },
    { "id":"7", "name": "Joan", "startDate": "23-10-2020", "endDate": "13-02-2021", "status": "unqualified", "description":"" },
    { "id":"8", "name": "Joan", "startDate": "23-10-2020", "endDate": "13-02-2021", "status": "unqualified", "description":"" }
]