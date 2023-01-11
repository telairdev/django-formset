import { createPopper, Instance } from '@popperjs/core';
import { Widget } from './helpers';
import styles from './DatePicker.scss';


enum ViewMode {
	weeks = 'w',
	months = 'm',
	years = 'y',
}


class Calendar extends Widget {
	private readonly inputElement: HTMLInputElement;
	private readonly calendarElement: HTMLElement;
	private readonly declaredStyles: HTMLStyleElement;
	private viewMode = ViewMode.weeks;
	// private monthView: HTMLUListElement | null = null;
	// private yearView: HTMLUListElement | null = null;
	private dropdownInstance?: Instance;
	private startDate!: Date;
	private isOpen = false;

	constructor(inputElement: HTMLInputElement, calendarElement: HTMLElement) {
		super(inputElement);
		this.inputElement = inputElement;
		this.calendarElement = calendarElement;
		this.declaredStyles = document.createElement('style');
		this.declaredStyles.innerText = styles;
		document.head.appendChild(this.declaredStyles);
		this.installEventHandlers();
		this.registerElement();
	}

	private installEventHandlers() {
		this.inputElement.addEventListener('focus', this.handleFocus);
		this.inputElement.addEventListener('blur', this.handleBlur);
		this.inputElement.addEventListener('change', this.handleChange);
		document.addEventListener('click', this.handleClick);
	}

	private setStartDate() {
		this.startDate = new Date(this.calendarElement.querySelector('time')?.getAttribute('datetime') ?? '');
		this.startDate.setTime(this.startDate.getTime() - this.startDate.getTimezoneOffset() * 60000);
	}

	private registerElement() {
		switch (this.viewMode) {
			case ViewMode.weeks:
				this.registerWeeksView();
				break;
			case ViewMode.months:
				this.registerMonthsView();
				break;
			case ViewMode.years:
				this.registerYearsView();
				break;
		}
	}

	private registerWeeksView() {
		this.calendarElement.querySelector('button.prev')?.addEventListener('click', event => this.changeMonth(-1), {once: true});
		this.calendarElement.querySelector('time')?.addEventListener('click', this.switchMonthsView, {once: true});
		this.calendarElement.querySelector('button.next')?.addEventListener('click', event => this.changeMonth(+1), {once: true});
		const today = new Date(Date.now());
		this.calendarElement.querySelectorAll('li[data-date]').forEach(elem => {
			const date = elem.getAttribute('data-date') ?? '';
			const date1 = new Date(date);
			const date2 = new Date(date1.getTime() + 86400000);
			elem.classList.toggle('today', today >= date1 && today < date2);
			elem.classList.toggle('selected', date === this.inputElement.value);
			elem.addEventListener('click', this.selectDate);
		});
		this.setStartDate();
	}

	private registerMonthsView() {
		this.calendarElement.querySelector('button.prev')?.addEventListener('click', event => this.changeYear(-1), {once: true});
		this.calendarElement.querySelector('time')?.addEventListener('click', this.switchYearsView, {once: true});
		this.calendarElement.querySelector('button.next')?.addEventListener('click', event => this.changeYear(+1), {once: true});
		this.calendarElement.querySelectorAll('li[data-date]').forEach(elem => {
			const date = elem.getAttribute('data-date') ?? '';
			elem.addEventListener('click', this.selectMonth);
		});
		this.setStartDate();
	}

	private registerYearsView() {
		this.calendarElement.querySelector('button.prev')?.addEventListener('click', event => this.changeYear(-1), {once: true});
		this.calendarElement.querySelector('button.next')?.addEventListener('click', event => this.changeYear(+1), {once: true});
		this.calendarElement.querySelectorAll('li[data-date]').forEach(elem => {
			const date = elem.getAttribute('data-date') ?? '';
			elem.addEventListener('click', this.selectYear);
		});
		this.setStartDate();
	}

	private handleClick = (event: Event) => {
		let element = event.target instanceof Element ? event.target : null;
		while (element) {
			if (element.isSameNode(this.calendarElement) || element.isSameNode(this.inputElement))
				return;
			element = element.parentElement;
		}
		this.isOpen = false;
		this.inputElement.blur();
		this.inputElement.setAttribute('aria-expanded', 'false')
		this.dropdownInstance?.destroy();
	}

	private handleFocus = (event: Event) => {
		this.dropdownInstance = createPopper(this.inputElement, this.calendarElement, {
			placement: 'bottom-start',
		});
		this.inputElement.setAttribute('aria-expanded', 'true')
		this.isOpen = true;
		const date = new Date(this.calendarElement.querySelector('time')?.getAttribute('datetime') ?? '');
		date.setTime(date.getTime() - date.getTimezoneOffset() * 60000);
		if (date.getTime() !== this.startDate.getTime()) {
			this.fetchCalendar(this.startDate);
		}
	}

	private handleBlur = (event: Event) => {
		if (this.isOpen) {
			this.inputElement.focus();
		}
	}

	private handleChange = (event: Event) => {
		const newDate = new Date(this.inputElement.value);
		if (isNaN(newDate.getTime())) {
			this.inputElement.value = 'yyyy-mm-dd';  // enforce a pattern validation error
		} else {
			this.fetchCalendar(newDate);
		}
	}

	private selectDate = (event: Event) => {
		if (event.target instanceof HTMLElement) {
			const target = event.target;
			const date = target.getAttribute('data-date') ?? '';
			this.calendarElement.querySelectorAll('li[data-date]').forEach(elem => {
				elem.classList.toggle('selected', elem.isSameNode(target));
			});
			this.inputElement.value = date;
			this.isOpen = false;
			this.inputElement.blur();
			this.inputElement.setAttribute('aria-expanded', 'false')
			this.inputElement.dispatchEvent(new Event('input'));
		 	this.dropdownInstance?.destroy();
			this.startDate = new Date(date);
			this.startDate.setUTCDate(1);
			this.startDate.setTime(this.startDate.getTime() - this.startDate.getTimezoneOffset() * 60000);
		}
	}

	private selectMonth = (event: Event) => {
		if (event.target instanceof HTMLLIElement) {
			const date = event.target.getAttribute('data-date') ?? '';
			this.viewMode = ViewMode.weeks;
			this.fetchCalendar(new Date(date));
		}
	}

	private selectYear = (event: Event) => {
		if (event.target instanceof HTMLTimeElement) {
			this.viewMode = ViewMode.months;
			this.fetchCalendar(new Date(this.startDate));
		}
	}

	private switchMonthsView = (event: Event) => {
		if (event.target instanceof HTMLTimeElement) {
			this.viewMode = ViewMode.months;
			this.fetchCalendar(new Date(this.startDate));
		}
	}

	private switchYearsView = (event: Event) => {
		if (event.target instanceof HTMLTimeElement) {
			this.viewMode = ViewMode.years;
			this.fetchCalendar(new Date(this.startDate));
		}
	}

	private async changeMonth(dir: number) {
		const newDate = new Date(this.startDate);
		newDate.setTime(newDate.getTime() - newDate.getTimezoneOffset() * 60000);
		if (this.startDate.getMonth() === 12 && dir > 0) {
			newDate.setUTCMonth(1);
			newDate.setUTCFullYear(newDate.getUTCFullYear() + 1);
		} else if (this.startDate.getMonth() === 1 && dir < 0) {
			newDate.setUTCMonth(12);
			newDate.setUTCFullYear(newDate.getUTCFullYear() - 1);
		} else {
			newDate.setUTCMonth(newDate.getUTCMonth() + dir);
		}
		this.fetchCalendar(newDate);
	}

	private async changeYear(dir: number) {
		const newDate = new Date(this.startDate);
		newDate.setTime(newDate.getTime() - newDate.getTimezoneOffset() * 60000);
		newDate.setUTCFullYear(newDate.getUTCFullYear() + dir);
		this.fetchCalendar(newDate);
	}

	private async fetchCalendar(newDate: Date) {
		const query = new URLSearchParams('calendar');
		query.set('date', newDate.toISOString().slice(0, 10));
		query.set('mode', this.viewMode);
		const response = await fetch(`${this.endpoint}?${query.toString()}`, {
			method: 'GET',
		});
		if (response.status === 200) {
			const innerHTML = await response.text();
			this.calendarElement.innerHTML = innerHTML;
			this.registerElement();
		} else {
			console.error(`Failed to fetch from ${this.endpoint} (status=${response.status})`);
		}

	}

	protected formResetted(event: Event) {}

	protected formSubmitted(event: Event) {}
}


export class DatePickerElement extends HTMLInputElement {
	private connectedCallback() {
		const fieldGroup = this.closest('django-field-group');
		if (!fieldGroup)
			throw new Error(`Attempt to initialize ${this} outside <django-formset>`);
		const calendarElement = fieldGroup.querySelector('[aria-label="calendar"]');
		if (!(calendarElement instanceof HTMLElement))
			throw new Error(`Attempt to initialize ${this} with sibling <ANY aria-label="calendar">`);
		new Calendar(this, calendarElement as HTMLElement);
	}
}
