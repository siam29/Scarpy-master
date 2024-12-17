import scrapy
import json
import re
import random
import os
import requests


class RandomCityHotelsSpider(scrapy.Spider):
    name = "hotel"
    allowed_domains = ["uk.trip.com"]
    start_urls = ["https://uk.trip.com/hotels/?locale=en-GB&curr=GBP"]

    def parse(self, response):
        script_data = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]/text()").get()
        if script_data:
            match = re.search(r"window\.IBU_HOTEL\s*=\s*(\{.*?\});", script_data, re.DOTALL)
            if match:
                json_data = match.group(1)
                try:
                    ibu_hotel_data = json.loads(json_data)
                    
                    inbound_cities = ibu_hotel_data.get("initData", {}).get("htlsData", {}).get("inboundCities", [])


                    outbound_cities = ibu_hotel_data.get("initData", {}).get("htlsData", {}).get("outboundCities", [])

                    cities_to_search = [inbound_cities, outbound_cities]

                    random_location_to_search = random.choice(cities_to_search)
                    
                    valid_cities = [
                        city for city in random_location_to_search 
                    ]
                    
                    if not valid_cities:
                        self.logger.warning("No cities with recommend hotels found")
                        return
                    
                    selected_city = random.choice(valid_cities)
                    
                    city_name = selected_city.get("name", "Unknown")
                    city_id = selected_city.get("id", "")
                    
                    if not city_id:
                        self.logger.warning(f"No ID found for city: {city_name}")
                        return
                    
                    city_hotels_url = f"https://uk.trip.com/hotels/list?city={city_id}"
                    
                    yield scrapy.Request(
                        url=city_hotels_url, 
                        callback=self.parse_city_hotels, 
                        meta={'city_name': city_name}
                    )
                
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON: {e}")
                except Exception as e:
                    self.logger.error(f"An unexpected error occurred: {e}")

    def parse_city_hotels(self, response):
        script_data = response.xpath("//script[contains(text(), 'window.IBU_HOTEL')]/text()").get()
        city_name = response.meta.get('city_name', 'Unknown')
        
        images_dir = os.path.join(os.getcwd(), 'image', city_name.lower().replace(' ', '_'))
        os.makedirs(images_dir, exist_ok=True)
        
        if script_data:
            match = re.search(r"window\.IBU_HOTEL\s*=\s*(\{.*?\});", script_data, re.DOTALL)
            if match:
                json_data = match.group(1)
                try:
                    ibu_hotel_data = json.loads(json_data)
                    
                    hotel_list = ibu_hotel_data.get("initData", {}).get("firstPageList", {}).get("hotelList", [])
                    
                    city_hotels = []
                    for hotel in hotel_list:
                        hotel_id = hotel.get("hotelBasicInfo", {}).get("hotelId", "")
                        hotel_name = hotel.get("hotelBasicInfo", {}).get("hotelName", "").replace(" ", "_")
                        image_url = hotel.get("hotelBasicInfo", {}).get("hotelImg", "")
                        
                        hotel_info = {
                            "city_name": city_name,
                            "property_title": hotel.get("hotelBasicInfo", {}).get("hotelName", ""),
                            "hotel_id": hotel_id,
                            "price": hotel.get("hotelBasicInfo", {}).get("price", ""),
                            "rating": hotel.get("commentInfo", {}).get("commentScore", ""),
                            "address": hotel.get("positionInfo", {}).get("positionName", ""),
                            "latitude": hotel.get("positionInfo", {}).get("coordinate", {}).get("lat", ""),
                            "longitude": hotel.get("positionInfo", {}).get("coordinate", {}).get("lng", ""),
                            "room_type": hotel.get("roomInfo", {}).get("physicalRoomName", ""),
                            "image": image_url  # Keep original image URL
                        }
                        
                        if image_url:
                            try:
                                image_filename = f"{hotel_id}_{hotel_name}.jpg"
                                image_path = os.path.join(images_dir, image_filename)
                                
                                # Download the image
                                response = requests.get(image_url)
                                if response.status_code == 200:
                                    with open(image_path, 'wb') as f:
                                        f.write(response.content)
                                    
                                    # Add local image path (using forward slashes for consistency)
                                    relative_image_path = os.path.join('image', city_name.lower().replace(' ', '_'), image_filename).replace('\\', '/')
                                    hotel_info['local_image_path'] = relative_image_path
                                    
                                    self.logger.info(f"Saved image for {hotel_name} at {image_path}")
                                else:
                                    self.logger.warning(f"Failed to download image for {hotel_name}")
                            except Exception as e:
                                self.logger.error(f"Error saving image for {hotel_name}: {e}")
                        
                        city_hotels.append(hotel_info)
                        yield hotel_info
                
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON: {e}")
                except Exception as e:
                    self.logger.error(f"An unexpected error occurred: {e}")