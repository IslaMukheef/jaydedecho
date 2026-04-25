"""
Router module - route planning and navigation guidance
Integrates with maps services for turn-by-turn directions
"""

import logging
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
import requests

try:
    from geopy.geocoders import Nominatim
except ImportError:
    Nominatim = None

logger = logging.getLogger(__name__)


@dataclass
class RouteStep:
    """Single step in a route"""
    instruction: str
    distance: float
    duration: float
    direction: str  # "forward", "left", "right", "slight-left", "slight-right", "uturn"


class Router:
    """Route planning and navigation"""

    def __init__(self, config):
        """Initialize router"""
        self.config = config
        self.current_route = None
        self.current_step_index = 0
        self.current_lat = config.default_location_lat
        self.current_lng = config.default_location_lng

        # Initialize geocoder
        self.geocoder = None
        if Nominatim:
            try:
                self.geocoder = Nominatim(user_agent="jaydeecho")
                logger.info("Geocoder initialized (Nominatim)")
            except Exception as e:
                logger.warning(f"Failed to initialize geocoder: {e}")
        else:
            logger.warning("geopy not installed. Address geocoding unavailable.")

        # Initialize routing service
        self._init_routing_service()
        logger.info(f"Router initialized at ({self.current_lat}, {self.current_lng})")

    def _init_routing_service(self):
        """Initialize OpenRouteService or fallback"""
        try:
            if self.config.openrouteservice_api_key:
                import openrouteservice
                self.ors_client = openrouteservice.Client(
                    key=self.config.openrouteservice_api_key
                )
                logger.info("OpenRouteService initialized for routing")
            else:
                logger.debug("No ORS API key. Will use mock routes.")
                self.ors_client = None
        except ImportError:
            logger.warning("openrouteservice not installed")
            self.ors_client = None
        except Exception as e:
            logger.error(f"Failed to initialize routing service: {e}")
            self.ors_client = None

    def _geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Convert address to coordinates"""
        if not self.geocoder:
            logger.debug(f"Geocoder unavailable. Using default location.")
            return None

        try:
            # Handle coordinate input (lat, lng)
            if "," in address:
                parts = address.split(",")
                if len(parts) == 2:
                    try:
                        lat = float(parts[0].strip())
                        lng = float(parts[1].strip())
                        if -90 <= lat <= 90 and -180 <= lng <= 180:
                            logger.info(f"Parsed coordinates: {lat}, {lng}")
                            return (lat, lng)
                    except ValueError:
                        pass

            logger.info(f"Geocoding: {address}")
            location = self.geocoder.geocode(address, timeout=5)

            if location:
                logger.info(f"Found: {location.latitude}, {location.longitude}")
                return (location.latitude, location.longitude)
            else:
                logger.warning(f"Address not found: {address}")
                return None

        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None

    def plan_route(self, destination: str) -> str:
        """
        Plan route to destination and return verbal announcement
        destination: address string or coordinates
        """
        try:
            logger.info(f"Planning route to: {destination}")

            # Geocode destination
            dest_coords = self._geocode_address(destination)

            if dest_coords:
                dest_lat, dest_lng = dest_coords
                logger.info(f"Route: ({self.current_lat}, {self.current_lng}) -> ({dest_lat}, {dest_lng})")

                # Try real routing service first
                if self.ors_client:
                    return self._route_with_ors(
                        (self.current_lng, self.current_lat),
                        (dest_lng, dest_lat),
                        destination
                    )
            else:
                logger.info("Could not geocode address, using mock route")

            return self._mock_route(destination)

        except Exception as e:
            logger.error(f"Error planning route: {e}")
            return f"Could not plan route to {destination}"

    def _route_with_ors(self, start: Tuple[float, float], end: Tuple[float, float], destination: str) -> str:
        """Plan route using OpenRouteService API"""
        try:
            logger.info("Using OpenRouteService for routing")

            coords = [start, end]
            route = self.ors_client.directions(
                coordinates=coords,
                profile='foot-walking',
                format='geojson'
            )

            if route and 'features' in route:
                feature = route['features'][0]
                properties = feature.get('properties', {})
                summary = properties.get('summary', {})

                distance_m = summary.get('distance', 0)
                duration_s = summary.get('duration', 0)

                distance_km = distance_m / 1000
                duration_min = int(duration_s / 60)

                announcement = f"Route to {destination}: "
                announcement += f"approximately {distance_km:.1f} kilometers, "
                announcement += f"about {duration_min} minutes walking. "
                announcement += "Start by heading towards your destination."

                logger.info(f"Route found: {distance_km:.1f} km, {duration_min} min")
                return announcement
            else:
                logger.warning("ORS returned invalid route")
                return self._mock_route(destination)

        except Exception as e:
            logger.error(f"ORS routing failed: {e}")
            return self._mock_route(destination)

    def _mock_route(self, destination: str) -> str:
        """Generate mock route for demo/testing"""
        logger.info(f"Using mock route to {destination}")

        steps = [
            RouteStep("Head forward", 150, 30, "forward"),
            RouteStep("Turn right", 300, 60, "right"),
            RouteStep("Continue straight", 200, 45, "forward"),
            RouteStep("Arrive at destination", 50, 15, "forward"),
        ]

        self.current_route = steps
        return self._format_route_announcement(steps, destination)

    def _format_route_announcement(self, steps: List[RouteStep], destination: str = "destination") -> str:
        """Format route steps as verbal announcement"""
        total_distance = sum(s.distance for s in steps)
        total_time = sum(s.duration for s in steps)

        announcement = f"Route to {destination}: approximately {int(total_distance)} meters, "
        announcement += f"about {int(total_time)} seconds walking. "
        if steps:
            announcement += f"First: {steps[0].instruction}"

        return announcement

    def get_next_step(self) -> Optional[str]:
        """Get current navigation step"""
        if not self.current_route or self.current_step_index >= len(self.current_route):
            return None

        step = self.current_route[self.current_step_index]
        return step.instruction

    def advance_step(self):
        """Move to next step in route"""
        if self.current_route:
            self.current_step_index += 1
            if self.current_step_index < len(self.current_route):
                logger.info(f"Step {self.current_step_index}: {self.get_next_step()}")

    def update_location(self, lat: float, lng: float):
        """Update current GPS location"""
        self.current_lat = lat
        self.current_lng = lng
        logger.debug(f"Location updated to ({lat}, {lng})")

    def announce_arrival(self) -> str:
        """Announce arrival at destination"""
        return "You have arrived at your destination."

    def get_route_summary(self) -> Optional[str]:
        """Get summary of current route"""
        if not self.current_route:
            return None

        total_distance = sum(s.distance for s in self.current_route)
        total_time = sum(s.duration for s in self.current_route)

        return f"Total distance: {int(total_distance)}m, estimated time: {int(total_time)}s"

