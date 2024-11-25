""" # Run model loop
        for i in range(1, runtime + 1):
            # Calculate vasopressin response
            if osmo > osmo_thresh:  # Vasopressin response
                vaso = min(v_grad * (osmo - osmo_thresh), v_max)
            else:
                vaso = 0
                # Adjust water loss rate based on vasopressin level
            waterloss = water_loss_base_rate 
            waterloss = max(waterloss, 0.005)  # Ensure water loss does not go negative
            water = water - (water * waterloss)  # Update water based on adjusted loss rate
            osmo = salt / water  # Recalculate osmolality after water update
            # Record model variables
            osmodata.water[i] = water
            osmodata.salt[i] = salt
            osmodata.osmo[i] = osmo
            osmodata.vaso[i] = vaso

 """

            