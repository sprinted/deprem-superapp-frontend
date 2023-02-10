from helpers.streamlit_helpers import streamlit_session_helper as session_helper, streamlit_helper as sh
from helpers.location_helpers import address_helper as ah
import numpy as np
from datetime import datetime, timedelta

from models import GLOBALS
from services import record_service
from helpers.location_helpers import folium_helper as fh


def first_page_province_changed():
    selected_province = session_helper.get_session("first_page_province")
    session_helper.set_session("first_page_selectable_districts",
                               np.array(session_helper.get_session("province_district_dict")[selected_province]))
    session_helper.set_session("first_page_district_index", 0)


def first_page_district_changed():
    selected_province = session_helper.get_session("first_page_province")
    selected_district = session_helper.get_session("first_page_district")

    address = f"{selected_province} {selected_district}"

    current_lat_long, _, _, _ = ah.GetCurrentLocationInfo(address)

    ah.SetAddressFields("first_page", current_lat_long=current_lat_long)


def first_page_address_changed():
    if session_helper.get_session("first_page_is_address_autofill"):
        address = session_helper.get_session("first_page_address")

        if len(address) > 5:
            current_lat_long, current_province, current_district, current_address = ah.GetCurrentLocationInfo(address)

            ah.SetAddressFields("first_page", current_lat_long, current_province, current_district, current_address)
    """
        if len(st.session_state['address']) > 5:
        my_province, my_district, my_open_address, my_latlong = ah.GetCurrentLocationInfo(
            address=st.session_state.address)
        if my_latlong is not None and len(my_latlong) == 2:
            if not st.session_state.is_address_autofill:
                my_open_address = None
            sh.SetAddressFields(my_province, my_district, my_latlong, my_open_address)

    :return:
    """
    pass


def first_page_on_submit_button_click(payload):
    payload["lat"] = session_helper.get_session("first_page_latitude")
    payload["lon"] = session_helper.get_session("first_page_longitude")
    # print(payload)

    response = record_service.CreateCallRecord(payload)

    if response is not None:
        sh.PopupSuccess("first_page")
    else:
        sh.PopupError("first_page", "Kaydınız eklenemedi! Lütfen zorunlu alanları konrol edin ve tekrar deneyin!")

    """
    diff_seconds = (datetime.now() - session_helper.get_session("first_page_message_send_date")).total_seconds()
    if diff_seconds > 120:
        if sh.ValidatePayload(payload):
            payload["zaman"] = datetime.now()
    """


def second_page_province_changed():
    selected_province = session_helper.get_session("second_page_province")
    session_helper.set_session("second_page_selectable_districts",
                               np.array(session_helper.get_session("province_district_dict")[selected_province]))
    session_helper.set_session("second_page_district_index", 0)


def second_page_district_changed():
    selected_province = session_helper.get_session("second_page_province")
    selected_district = session_helper.get_session("second_page_district")

    address = f"{selected_province} {selected_district}"

    current_lat_long, _, _, _ = ah.GetCurrentLocationInfo(address)

    ah.SetAddressFields("second_page", current_lat_long=current_lat_long)


def second_page_start_date_filter_changed():
    session_helper.set_session("second_page_start_date_value",
                               session_helper.get_session("second_page_start_date_filter"))
    if session_helper.get_session("second_page_start_date_value") > session_helper.get_session(
            "second_page_end_date_filter"):
        session_helper.set_session("second_page_end_date_value",
                                   session_helper.get_session("second_page_start_date_value") + timedelta(days=1))


def second_page_end_date_filter_changed():
    session_helper.set_session("second_page_end_date_value", session_helper.get_session("second_page_end_date_filter"))
    if session_helper.get_session("second_page_end_date_value") < session_helper.get_session(
            "second_page_start_date_filter"):
        session_helper.set_session("second_page_start_date_value",
                                   session_helper.get_session("second_page_end_date_value") + timedelta(days=-1))


def second_page_filter_click():
    il, ilce, isim, baslangic_tarihi, bitis_tarihi, gereksinimler, telefon, notlar = __get_second_page_current_field_values()
    session_helper.set_session("is_filtered", True)

    sh.SetCallRecordsState(page_size=GLOBALS.PAGE_SIZE, province=il, district=ilce, name=isim, needs=gereksinimler,
                           notes=notlar, phone=telefon, start_date=baslangic_tarihi, end_date=bitis_tarihi)

    # print([[res["lat"], res["lon"]]for res in session_helper.get_session("second_page_last_call_records_raw")])

    session_helper.set_session("second_page_map", fh.CreateMultiMarkerMap(
        [[res["lat"], res["lon"]] for res in session_helper.get_session("second_page_last_call_records_raw")]))
    """
    record_ids = ','.join([str(i[7]) for i in last_records])

    st.session_state.province_record_counts_str = sh.GetProvinceRecordCounts(record_ids)
    """


def second_page_refresh_click():
    pass


def second_page_pager_button_click(i):
    il, ilce, isim, baslangic_tarihi, bitis_tarihi, gereksinimler, telefon, notlar = __get_second_page_current_field_values()

    if not session_helper.get_session("is_filtered"):
        baslangic_tarihi = None
        bitis_tarihi = None

    sh.SetCallRecordsState(page_size=GLOBALS.PAGE_SIZE, page=i, province=il, district=ilce, needs=gereksinimler,
                           notes=notlar, phone=telefon, start_date=baslangic_tarihi, end_date=bitis_tarihi)


def __get_second_page_current_field_values():
    il = session_helper.get_session("second_page_province")
    ilce = session_helper.get_session("second_page_district")
    isim = session_helper.get_session("second_page_name")
    baslangic_tarihi = session_helper.get_session("second_page_start_date_filter")
    bitis_tarihi = session_helper.get_session("second_page_end_date_filter")
    notlar = session_helper.get_session("second_page_notes")
    gereksinimler = session_helper.get_session("second_page_needs")
    telefon = session_helper.get_session("second_page_phone")

    baslangic_tarihi = baslangic_tarihi.strftime("%Y-%m-%d %H:%M:%S") + ".0000"
    bitis_tarihi = bitis_tarihi.strftime("%Y-%m-%d %H:%M:%S") + ".0000"

    return il, ilce, isim, baslangic_tarihi, bitis_tarihi, gereksinimler, telefon, notlar


def third_page_province_changed():
    selected_province = session_helper.get_session("third_page_province")
    session_helper.set_session("third_page_selectable_districts",
                               np.array(session_helper.get_session("province_district_dict")[selected_province]))
    session_helper.set_session("third_page_district_index", 0)


def third_page_district_changed():
    selected_province = session_helper.get_session("third_page_province")
    selected_district = session_helper.get_session("third_page_district")

    address = f"{selected_province} {selected_district}"

    current_lat_long, _, _, _ = ah.GetCurrentLocationInfo(address)

    ah.SetAddressFields("third_page", current_lat_long=current_lat_long)


def third_page_address_changed():
    if session_helper.get_session("third_page_is_address_autofill"):
        address = session_helper.get_session("third_page_address")

        if len(address) > 5:
            current_lat_long, current_province, current_district, current_address = ah.GetCurrentLocationInfo(address)

            ah.SetAddressFields("third_page", current_lat_long, current_province, current_district, current_address)
    """
        if len(st.session_state['address']) > 5:
        my_province, my_district, my_open_address, my_latlong = ah.GetCurrentLocationInfo(
            address=st.session_state.address)
        if my_latlong is not None and len(my_latlong) == 2:
            if not st.session_state.is_address_autofill:
                my_open_address = None
            sh.SetAddressFields(my_province, my_district, my_latlong, my_open_address)

    :return:
    """
    pass


def third_page_on_submit_button_click(payload):
    payload["lat"] = session_helper.get_session("third_page_latitude")
    payload["lon"] = session_helper.get_session("third_page_longitude")
    # print(payload)

    response = record_service.CreateHelperRecord(payload)

    if response is not None:
        sh.PopupSuccess("third_page")
    else:
        sh.PopupError("third_page", "Kaydınız eklenemedi! Lütfen zorunlu alanları konrol edin ve tekrar deneyin!")

    """
    diff_seconds = (datetime.now() - session_helper.get_session("third_page_message_send_date")).total_seconds()
    if diff_seconds > 120:
        if sh.ValidatePayload(payload):
            payload["zaman"] = datetime.now()
    """
