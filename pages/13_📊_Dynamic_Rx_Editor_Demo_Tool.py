import streamlit as st
import pandas as pd
import numpy as np

# Title and description
st.title("🌾 Dynamic Fertilizer Rate Adjustment Tool")

# Add an expander with explanation
with st.expander("ℹ️ How This Tool Works"):
    st.markdown(
        """
        ### How to Use This Tool
        1. **Review the Original Fertilizer Rates**: The initial 10x10 grid shows the default fertilizer rates for each cell.
        2. **Set Your Adjustment Target**: Choose a scaling method and enter your desired target value.
        3. **Select the Scaling Approach**: Currently, only "Equal Scaling" is available. "Bell Curve Scaling" is coming soon! 🚀
        4. **Set Minimum and Maximum Rates**: Specify the minimum and maximum allowable rates to enforce constraints.
        5. **Apply Adjustments**: Click the "Apply Adjustments" button to adjust the rates based on your inputs.

        ### What Happens Behind the Scenes
        - The tool iteratively adjusts the fertilizer rates to meet your target value.
        - It applies scaling factors while respecting the minimum and maximum rate constraints.
        - The process continues until the target is achieved within a small tolerance or no further adjustments can be made.

        ### Note
        - The "Bell Curve Scaling" option is not yet available. Stay tuned! 🚧
        """
    )

# Initialize a 10x10 grid with values from null to 100
if 'grid_data' not in st.session_state:
    st.session_state.grid_data = np.random.choice([None] + list(range(0, 101)), size=(10, 10))

# Display the initial grid as a dataframe
grid_df = pd.DataFrame(
    st.session_state.grid_data,
    columns=[f'Col {i+1}' for i in range(10)],
    index=[f'Row {i+1}' for i in range(10)]
)
st.subheader("🌱 Original Fertilizer Rates (lbs/acre)")
st.dataframe(grid_df)

# Flatten and drop null and zero values
valid_values = grid_df.stack()
valid_values = valid_values[~valid_values.isnull() & (valid_values != 0)]

# Calculate and display current default values
current_total_product = valid_values.sum()
cost_per_pound = 10  # Cost per pound of product (urea)
current_total_cost = current_total_product * cost_per_pound
current_avg_rate = current_total_product / len(valid_values)  # Average rate excluding null values

st.markdown(
    f"""### 📊 Current Default Values
    - **Total Product (urea)**: {current_total_product:.2f} lbs
    - **Total Cost**: ${current_total_cost:.2f}
    - **Average Rate per Acre**: {current_avg_rate:.2f} lbs/acre
    - **Cost per Pound of Product (urea)**: ${cost_per_pound:.2f}
    """
)

# User input for adjustment targets
scaling_method = st.selectbox("Select Scaling Method", [
    "Total Product (urea):",
    "Total Cost:",
    "Average Rate per Acre:",
    "Spend Per Acre (dollars per acre):"
])
adjustment_value = st.number_input(f"Enter Desired Value for {scaling_method}", min_value=0.0, step=1.0)

# Scaling Approach
scaling_approach = st.selectbox(
    "Select Scaling Approach",
    ["Equal Scaling"],  # Only "Equal Scaling" is available
    help="Bell Curve Scaling is coming soon! 🚧"
)

# Min/Max Inputs (Optional)
min_rate = st.number_input(
    "Minimum Rate (lbs/acre)", min_value=0.0, step=1.0, value=0.0, format="%.2f"
)
max_rate = st.number_input(
    "Maximum Rate (lbs/acre)", min_value=0.0, step=1.0, value=100.0, format="%.2f"
)

# Apply Adjustments Button
if st.button("Apply Adjustments"):
    # Define tolerance level
    tolerance = 1e-2  # Adjust as needed

    # Initialize variables
    valid_values = valid_values.astype(float)  # Ensure values are float for calculations
    locked_mask = pd.Series(False, index=valid_values.index)
    iteration = 0
    max_iterations = 100  # To prevent infinite loops

    epsilon = 1e-6  # For floating-point comparison

    while iteration < max_iterations:
        iteration += 1

        # Exclude locked cells using the mask
        adjustable_values = valid_values[~locked_mask]

        # Check if there are adjustable cells left
        if adjustable_values.empty:
            break

        # Recalculate totals for adjustable cells
        total_area = len(adjustable_values)
        current_total_product = adjustable_values.sum()
        current_avg_rate = current_total_product / total_area

        # Recalculate the adjustment factor
        if scaling_method == "Total Product (urea):":
            total_current = valid_values.sum()
            total_adjustable = adjustable_values.sum()
            remaining_adjustment = adjustment_value - total_current
            adjustment_factor = (remaining_adjustment / (total_adjustable + 1e-6)) + 1
            adjustment_factor = max(adjustment_factor, 0.0)  # Ensure it's not negative

        elif scaling_method == "Total Cost:":
            total_current = valid_values.sum() * cost_per_pound
            total_adjustable = adjustable_values.sum() * cost_per_pound
            remaining_adjustment = adjustment_value - total_current
            adjustment_factor = (remaining_adjustment / (total_adjustable + 1e-6)) + 1
            adjustment_factor = max(adjustment_factor, 0.0)

        elif scaling_method == "Average Rate per Acre:":
            total_current = valid_values.mean()
            total_adjustable = adjustable_values.mean()
            remaining_adjustment = adjustment_value - total_current
            adjustment_factor = (remaining_adjustment / (total_adjustable + 1e-6)) + 1
            adjustment_factor = max(adjustment_factor, 0.0)

        elif scaling_method == "Spend Per Acre (dollars per acre):":
            total_current = (valid_values.sum() * cost_per_pound) / len(valid_values)
            total_adjustable = (adjustable_values.sum() * cost_per_pound) / len(adjustable_values)
            remaining_adjustment = adjustment_value - total_current
            adjustment_factor = (remaining_adjustment / (total_adjustable + 1e-6)) + 1
            adjustment_factor = max(adjustment_factor, 0.0)

        else:
            st.error("Unknown scaling method selected.")
            break

        # Apply Scaling
        if scaling_approach == "Equal Scaling":
            adjusted_values = adjustable_values * adjustment_factor
        else:
            st.warning("Bell Curve Scaling is not available yet.")
            break

        # Enforce Min/Max Constraints
        adjusted_values_clipped = adjusted_values.clip(lower=min_rate, upper=max_rate)

        # Identify newly locked cells using epsilon
        newly_locked = (
            ((adjusted_values_clipped - min_rate).abs() < epsilon) |
            ((adjusted_values_clipped - max_rate).abs() < epsilon)
        ) & (~locked_mask.loc[adjusted_values_clipped.index])

        # Update locked mask
        locked_mask.loc[newly_locked.index] = True

        # Update valid_values with adjusted values
        valid_values.loc[adjusted_values_clipped.index] = adjusted_values_clipped

        # Calculate the adjusted total based on the scaling method
        if scaling_method == "Total Product (urea):":
            adjusted_total = valid_values.sum()
            unit = "lbs"
        elif scaling_method == "Total Cost:":
            adjusted_total = valid_values.sum() * cost_per_pound
            unit = "$"
        elif scaling_method == "Average Rate per Acre:":
            adjusted_total = valid_values.mean()
            unit = "lbs/acre"
        elif scaling_method == "Spend Per Acre (dollars per acre):":
            adjusted_total = (valid_values.sum() * cost_per_pound) / len(valid_values)
            unit = "$/acre"
        else:
            st.error("Unknown scaling method selected.")
            break

        difference = abs(adjusted_total - adjustment_value)

        # Check if the adjusted total is within the tolerance
        if difference <= tolerance:
            break

        # If no adjustable cells are left, break
        if adjustable_values.empty:
            break

        # Optionally, add a check for no significant change
        if abs(adjustment_factor - 1) < epsilon:
            break

    # Update the DataFrame with adjusted values
    adjusted_grid_df = grid_df.copy()

    # Unstack the adjusted values back into the grid format
    adjusted_values_unstacked = valid_values.unstack()

    # Update adjusted_grid_df only at the positions of adjusted_values_unstacked
    adjusted_grid_df.update(adjusted_values_unstacked)

    # Display the adjusted grid
    st.subheader("🌿 Adjusted Fertilizer Rates (lbs/acre)")
    st.dataframe(adjusted_grid_df)

    # Summary Statistics
    adjusted_total_product = valid_values.sum()
    adjusted_total_cost = adjusted_total_product * cost_per_pound
    adjusted_avg_rate = adjusted_total_product / len(valid_values)

    st.markdown(
        f"""### 📈 Summary After Adjustment
        - **Total Product (urea)**: {adjusted_total_product:.2f} lbs
        - **Total Cost**: ${adjusted_total_cost:.2f}
        - **Average Rate per Acre**: {adjusted_avg_rate:.2f} lbs/acre
        - **Adjustment Factor Applied**: {adjustment_factor:.4f}
        - **Iterations**: {iteration}
        """
    )

    # Display a friendly message
    if difference <= tolerance:
        st.success(f"🎉 The target value of {adjustment_value:.2f} {unit} has been achieved!")
    else:
        st.warning(f"⚠️ Unable to reach the target value of {adjustment_value:.2f} {unit} due to constraints.")