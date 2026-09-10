import React, { useEffect, useRef, useState } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { Dropdown } from 'primereact/dropdown';
import { InputText } from 'primereact/inputtext';
import { Calendar } from 'primereact/calendar';
import { Toast } from 'primereact/toast';
import { Toolbar } from 'primereact/toolbar';
import { Tag } from 'primereact/tag';
import { FilterMatchMode } from 'primereact/api';
import { classNames } from 'primereact/utils';

const STATUS_OPTIONS = ['Qualified', 'New', 'Unqualified', 'Pending'];
const STATUS_SEVERITY = {
    Qualified: 'success',
    New: 'info',
    Unqualified: 'danger',
    Pending: 'warning'
};

const INITIAL_TASKS = [
    { id: 12, name: 'Ahmed B.',    startDate: '2021-02-18', endDate: '2021-09-22', status: 'Pending' },
    { id: 6,  name: 'Asiya M.',    startDate: '2020-07-19', endDate: '2021-02-18', status: 'New' },
    { id: 10, name: 'Carlos V.',   startDate: '2021-03-05', endDate: '2021-12-01', status: 'Qualified' },
    { id: 15, name: 'Dmitri N.',   startDate: '2020-08-20', endDate: '2021-03-28', status: 'Unqualified' },
    { id: 4,  name: 'Emmanuel X.', startDate: '2020-12-23', endDate: '2021-05-21', status: 'Unqualified' },
    { id: 5,  name: 'Jean G.',     startDate: '2020-10-02', endDate: '2021-03-03', status: 'New' },
    { id: 1,  name: 'Joan F.',     startDate: '2020-10-23', endDate: '2021-02-13', status: 'Qualified' },
    { id: 8,  name: 'Joan P.',     startDate: '2020-10-23', endDate: '2021-02-13', status: 'Unqualified' },
    { id: 7,  name: 'Joan R.',     startDate: '2020-10-23', endDate: '2021-02-13', status: 'Unqualified' },
    { id: 11, name: 'Lena W.',     startDate: '2020-09-14', endDate: '2021-04-30', status: 'New' },
    { id: 2,  name: 'Marta C.',    startDate: '2021-01-11', endDate: '2021-07-16', status: 'Pending' },
    { id: 3,  name: 'Nikos T.',    startDate: '2020-11-09', endDate: '2021-08-14', status: 'Qualified' },
    { id: 9,  name: 'Olga K.',     startDate: '2021-02-01', endDate: '2021-10-06', status: 'Pending' },
    { id: 13, name: 'Rita P.',     startDate: '2020-06-18', endDate: '2021-01-22', status: 'New' },
    { id: 14, name: 'Stefan D.',   startDate: '2021-04-12', endDate: '2021-11-30', status: 'Qualified' }
];

const emptyForm = {
    id: null,
    name: '',
    startDate: '',
    endDate: '',
    status: 'Pending'
};

const formatDate = (value) => {
    if (!value) return '';
    const [year, month, day] = value.split('-');
    return `${day}/${month}/${year}`;
};

const toIsoDate = (date) => {
    if (!date) return '';
    if (typeof date === 'string') return date;
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
};

const fromIsoDate = (iso) => {
    if (!iso) return null;
    const [year, month, day] = iso.split('-').map(Number);
    return new Date(year, (month || 1) - 1, day || 1);
};

const Crud = () => {
    const [tasks, setTasks] = useState(INITIAL_TASKS);
    const [selected, setSelected] = useState([]);
    const [globalFilter, setGlobalFilter] = useState('');
    const [statusFilter, setStatusFilter] = useState(null);
    const [filters, setFilters] = useState({
        global: { value: '', matchMode: FilterMatchMode.CONTAINS },
        status: { value: null, matchMode: FilterMatchMode.EQUALS }
    });

    const [taskDialog, setTaskDialog] = useState(false);
    const [deleteDialog, setDeleteDialog] = useState(false);
    const [deleteSelectedDialog, setDeleteSelectedDialog] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [form, setForm] = useState(emptyForm);

    const toast = useRef(null);
    const dt = useRef(null);

    useEffect(() => {
        setFilters((prev) => ({
            ...prev,
            global: { ...prev.global, value: globalFilter },
            status: { ...prev.status, value: statusFilter }
        }));
    }, [globalFilter, statusFilter]);

    /* ---------- Dialog helpers ---------- */

    const openNew = () => {
        setForm(emptyForm);
        setSubmitted(false);
        setTaskDialog(true);
    };

    const openEdit = (task) => {
        setForm({ ...task });
        setSubmitted(false);
        setTaskDialog(true);
    };

    const hideDialog = () => {
        setTaskDialog(false);
        setSubmitted(false);
    };

    /* ---------- Persist ---------- */

    const saveTask = () => {
        setSubmitted(true);

        if (!form.name.trim() || !form.startDate || !form.endDate || !form.status) {
            return;
        }

        if (new Date(form.startDate) > new Date(form.endDate)) {
            toast.current?.show({
                severity: 'error',
                summary: 'Invalid dates',
                detail: 'Start Date cannot be later than End Date',
                life: 3000
            });
            return;
        }

        if (form.id != null && tasks.some((t) => t.id === form.id)) {
            setTasks((current) => current.map((t) => (t.id === form.id ? { ...form } : t)));
            toast.current?.show({
                severity: 'success',
                summary: 'Updated',
                detail: `Task "${form.name}" updated`,
                life: 2200
            });
        } else {
            const nextId = tasks.reduce((max, t) => Math.max(max, t.id), 0) + 1;
            setTasks((current) => [...current, { ...form, id: nextId }]);
            toast.current?.show({
                severity: 'success',
                summary: 'Created',
                detail: `Task "${form.name}" created`,
                life: 2200
            });
        }

        setTaskDialog(false);
        setForm(emptyForm);
        setSubmitted(false);
    };

    /* ---------- Delete ---------- */

    const confirmDelete = (task) => {
        setForm({ ...task });
        setDeleteDialog(true);
    };

    const doDelete = () => {
        setTasks((current) => current.filter((t) => t.id !== form.id));
        setSelected((current) => current.filter((t) => t.id !== form.id));
        setDeleteDialog(false);
        toast.current?.show({
            severity: 'warn',
            summary: 'Deleted',
            detail: `Task "${form.name}" deleted`,
            life: 2200
        });
        setForm(emptyForm);
    };

    const confirmDeleteSelected = () => setDeleteSelectedDialog(true);

    const doDeleteSelected = () => {
        const ids = new Set(selected.map((t) => t.id));
        setTasks((current) => current.filter((t) => !ids.has(t.id)));
        setSelected([]);
        setDeleteSelectedDialog(false);
        toast.current?.show({
            severity: 'warn',
            summary: 'Deleted',
            detail: `${ids.size} task(s) deleted`,
            life: 2200
        });
    };

    /* ---------- Export ---------- */

    const exportCSV = () => dt.current?.exportCSV();

    /* ---------- Form ---------- */

    const onFieldChange = (field, value) => {
        setForm((current) => ({ ...current, [field]: value }));
    };

    /* ---------- Rendering ---------- */

    const statusBody = (rowData) => (
        <Tag value={rowData.status} severity={STATUS_SEVERITY[rowData.status] || 'info'} />
    );

    const actionsBody = (rowData) => (
        <div className="flex gap-2 justify-content-center">
            <Button
                icon="pi pi-pencil"
                rounded
                outlined
                aria-label={`Edit ${rowData.name}`}
                onClick={() => openEdit(rowData)}
            />
            <Button
                icon="pi pi-trash"
                rounded
                outlined
                severity="danger"
                aria-label={`Delete ${rowData.name}`}
                onClick={() => confirmDelete(rowData)}
            />
        </div>
    );

    const dateBody = (field) => (rowData) => formatDate(rowData[field]);

    const leftToolbar = (
        <div className="flex flex-wrap gap-2">
            <Button label="Add Task" icon="pi pi-plus" severity="success" onClick={openNew} />
            <Button
                label="Delete"
                icon="pi pi-trash"
                severity="danger"
                outlined
                onClick={confirmDeleteSelected}
                disabled={!selected || selected.length === 0}
            />
        </div>
    );

    const rightToolbar = (
        <div className="flex flex-wrap gap-2 align-items-center">
            <Dropdown
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.value)}
                options={STATUS_OPTIONS}
                placeholder="All status"
                showClear
                className="w-10rem"
            />
            <span className="p-input-icon-left">
                <i className="pi pi-search" />
                <InputText
                    value={globalFilter}
                    onChange={(e) => setGlobalFilter(e.target.value)}
                    placeholder="Search..."
                />
            </span>
            <Button icon="pi pi-upload" label="Export" outlined onClick={exportCSV} />
        </div>
    );

    const header = (
        <div className="flex flex-wrap justify-content-between align-items-center gap-3">
            <div>
                <h2 className="m-0">CRUD Table</h2>
                <span className="text-color-secondary">
                    {tasks.length} records · {selected.length} selected
                </span>
            </div>
        </div>
    );

    const taskDialogFooter = (
        <>
            <Button label="Cancel" icon="pi pi-times" text onClick={hideDialog} />
            <Button label="Save" icon="pi pi-check" onClick={saveTask} />
        </>
    );

    const deleteDialogFooter = (
        <>
            <Button label="No" icon="pi pi-times" text onClick={() => setDeleteDialog(false)} />
            <Button label="Yes" icon="pi pi-check" severity="danger" onClick={doDelete} />
        </>
    );

    const deleteSelectedDialogFooter = (
        <>
            <Button label="No" icon="pi pi-times" text onClick={() => setDeleteSelectedDialog(false)} />
            <Button label="Yes" icon="pi pi-check" severity="danger" onClick={doDeleteSelected} />
        </>
    );

    return (
        <div className="card">
            <Toast ref={toast} />

            <Toolbar className="mb-3" start={leftToolbar} end={rightToolbar} />

            <DataTable
                ref={dt}
                value={tasks}
                selection={selected}
                onSelectionChange={(e) => setSelected(e.value)}
                dataKey="id"
                paginator
                rows={10}
                rowsPerPageOptions={[5, 10, 25, 50]}
                paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
                currentPageReportTemplate="Showing {first} to {last} of {totalRecords}"
                filters={filters}
                globalFilterFields={['name', 'status']}
                header={header}
                emptyMessage="No records found"
                stripedRows
                removableSort
            >
                <Column selectionMode="multiple" headerStyle={{ width: '3rem' }} />
                <Column field="id" header="ID" sortable style={{ width: '4rem' }} />
                <Column field="name" header="Name" sortable />
                <Column field="startDate" header="Start Date" body={dateBody('startDate')} sortable />
                <Column field="endDate" header="End Date" body={dateBody('endDate')} sortable />
                <Column field="status" header="Status" body={statusBody} sortable />
                <Column body={actionsBody} headerStyle={{ width: '8rem' }} bodyStyle={{ textAlign: 'center' }} />
            </DataTable>

            {/* Edit / Create */}
            <Dialog
                visible={taskDialog}
                style={{ width: '32rem' }}
                breakpoints={{ '960px': '75vw', '641px': '95vw' }}
                header={form.id != null ? 'Edit Task' : 'New Task'}
                modal
                onHide={hideDialog}
                footer={taskDialogFooter}
            >
                <div className="field">
                    <label htmlFor="name" className="font-bold">Name</label>
                    <InputText
                        id="name"
                        value={form.name}
                        onChange={(e) => onFieldChange('name', e.target.value)}
                        autoFocus
                        className={classNames({ 'p-invalid': submitted && !form.name.trim() })}
                    />
                    {submitted && !form.name.trim() && <small className="p-error">Name is required.</small>}
                </div>

                <div className="formgrid grid">
                    <div className="field col">
                        <label htmlFor="startDate" className="font-bold">Start Date</label>
                        <Calendar
                            id="startDate"
                            value={fromIsoDate(form.startDate)}
                            onChange={(e) => onFieldChange('startDate', toIsoDate(e.value))}
                            dateFormat="dd/mm/yy"
                            showIcon
                            className={classNames({ 'p-invalid': submitted && !form.startDate })}
                        />
                        {submitted && !form.startDate && <small className="p-error">Start Date is required.</small>}
                    </div>

                    <div className="field col">
                        <label htmlFor="endDate" className="font-bold">End Date</label>
                        <Calendar
                            id="endDate"
                            value={fromIsoDate(form.endDate)}
                            onChange={(e) => onFieldChange('endDate', toIsoDate(e.value))}
                            dateFormat="dd/mm/yy"
                            showIcon
                            className={classNames({ 'p-invalid': submitted && !form.endDate })}
                        />
                        {submitted && !form.endDate && <small className="p-error">End Date is required.</small>}
                    </div>
                </div>

                <div className="field">
                    <label htmlFor="status" className="font-bold">Status</label>
                    <Dropdown
                        id="status"
                        value={form.status}
                        onChange={(e) => onFieldChange('status', e.value)}
                        options={STATUS_OPTIONS}
                        placeholder="Select a status"
                        className={classNames({ 'p-invalid': submitted && !form.status })}
                    />
                </div>
            </Dialog>

            {/* Delete one */}
            <Dialog
                visible={deleteDialog}
                style={{ width: '28rem' }}
                header="Confirm"
                modal
                onHide={() => setDeleteDialog(false)}
                footer={deleteDialogFooter}
            >
                <div className="flex align-items-center gap-3">
                    <i className="pi pi-exclamation-triangle text-3xl" style={{ color: 'var(--orange-500, #E8903E)' }} />
                    <span>
                        Are you sure you want to delete <b>{form.name}</b>?
                    </span>
                </div>
            </Dialog>

            {/* Delete bulk */}
            <Dialog
                visible={deleteSelectedDialog}
                style={{ width: '28rem' }}
                header="Confirm"
                modal
                onHide={() => setDeleteSelectedDialog(false)}
                footer={deleteSelectedDialogFooter}
            >
                <div className="flex align-items-center gap-3">
                    <i className="pi pi-exclamation-triangle text-3xl" style={{ color: 'var(--orange-500, #E8903E)' }} />
                    <span>Delete {selected.length} selected task(s)?</span>
                </div>
            </Dialog>
        </div>
    );
};

export default Crud;
